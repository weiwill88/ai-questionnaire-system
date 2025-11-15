"""
FastAPI 主应用
AI应用需求调研系统后端
"""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv
import csv
import io

from models import (
    QuestionnaireSubmit, 
    SubmitResponse, 
    StatsResponse,
    ErrorResponse
)
from database import db
from llm_analyzer import llm_analyzer

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="AI应用需求调研系统 API",
    description="上海交通大学高级金融学院 MBA 课程问卷系统",
    version="1.0.0"
)

# 配置CORS
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins != ['*'] else ['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================================================
# API端点
# ================================================================

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "AI应用需求调研系统 API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "submit": "POST /api/submit",
            "stats": "GET /api/stats",
            "export": "GET /api/export"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


@app.post("/api/submit", response_model=SubmitResponse)
async def submit_questionnaire(
    data: QuestionnaireSubmit,
    request: Request
):
    """
    接收问卷提交
    
    Args:
        data: 问卷数据
        request: HTTP请求对象
        
    Returns:
        提交成功响应，包含响应ID
        
    Raises:
        HTTPException: 提交失败时返回错误
    """
    try:
        # 准备插入数据库的数据
        db_data = {
            'session_id': data.session_id,
            'q1_industry': data.q1_industry,
            'q1_industry_other': data.q1_industry_other,
            'q2_role': data.q2_role,
            'q2_role_other': data.q2_role_other,
            'q3_digital_habit': data.q3_digital_habit,
            'q4_ai_self_position': data.q4_ai_self_position,
            'q5_ai_usage': data.q5_ai_usage,
            'q6_org_stage': data.q6_org_stage,
            'q7_personal_role': data.q7_personal_role,
            'q8_pain_points': data.q8_pain_points,
            'q9_attitude': data.q9_attitude,
            'q10_constraints': data.q10_constraints,
            'completion_time_seconds': data.completion_time_seconds,
            'device_type': data.device_type,
            'user_agent': data.user_agent,
            'ip_hash': data.ip_hash
        }
        
        # 插入数据库
        response_id = await db.insert_response(db_data)
        
        return SubmitResponse(
            success=True,
            message="提交成功",
            id=response_id
        )
        
    except Exception as e:
        error_msg = str(e)
        
        # 重复提交错误
        if "重复提交" in error_msg:
            raise HTTPException(
                status_code=409,
                detail="您已经提交过问卷，请勿重复提交"
            )
        
        # 其他错误
        raise HTTPException(
            status_code=500,
            detail=f"提交失败: {error_msg}"
        )


@app.get("/api/stats")
async def get_statistics(session_id: str):
    """
    获取问卷统计数据
    
    Args:
        session_id: 场次ID（查询参数）
        
    Returns:
        统计数据，包含人数、分布等
        
    Raises:
        HTTPException: 查询失败时返回错误
    """
    try:
        stats = await db.get_statistics(session_id)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计失败: {str(e)}"
        )


@app.get("/api/export")
async def export_data(session_id: str):
    """
    导出问卷数据为CSV
    
    Args:
        session_id: 场次ID（查询参数）
        
    Returns:
        CSV文件流
        
    Raises:
        HTTPException: 导出失败时返回错误
    """
    try:
        # 获取所有回答
        responses = await db.get_all_responses(session_id)
        
        if not responses:
            raise HTTPException(
                status_code=404,
                detail="未找到数据"
            )
        
        # 创建CSV
        output = io.StringIO()
        
        # 定义CSV列
        fieldnames = [
            'id', 'created_at', 'session_id',
            'q1_industry', 'q1_industry_other',
            'q2_role', 'q2_role_other',
            'q3_digital_habit', 'q4_ai_self_position',
            'q5_ai_usage', 'q6_org_stage', 'q7_personal_role',
            'q8_pain_points', 'q9_attitude', 'q10_constraints',
            'completion_time_seconds', 'device_type'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        # 写入数据
        for response in responses:
            # 将数组转换为字符串
            if response.get('q8_pain_points'):
                response['q8_pain_points'] = ','.join(response['q8_pain_points'])
            if response.get('q10_constraints'):
                response['q10_constraints'] = ','.join(response['q10_constraints'])
            
            writer.writerow(response)
        
        # 转换为字节流
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=questionnaire_{session_id}.csv"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出失败: {str(e)}"
        )


@app.post("/api/analyze")
async def analyze_questionnaire(request: Request):
    """
    AI分析问卷结果
    
    请求体:
    {
        "session_id": "SJTU_SAIF_20251114",
        "use_simple_prompt": false  # 可选，是否使用简化提示词
    }
    
    返回:
    {
        "success": true,
        "data": {
            "session_id": "...",
            "analysis": "...",  # AI分析结果（Markdown格式）
            "model": "...",
            "total_responses": 20
        }
    }
    """
    try:
        # 检查LLM分析器是否可用
        if llm_analyzer is None:
            raise HTTPException(
                status_code=503,
                detail="AI分析功能未配置，请在.env中添加OPENROUTER_API_KEY"
            )
        
        # 解析请求体
        body = await request.json()
        session_id = body.get('session_id', os.getenv('SESSION_ID'))
        use_simple_prompt = body.get('use_simple_prompt', False)
        
        if not session_id:
            raise HTTPException(
                status_code=400,
                detail="缺少session_id参数"
            )
        
        # 获取统计数据
        stats = await db.get_statistics(session_id)
        
        if not stats or stats.get('total_responses', 0) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"会话 {session_id} 没有问卷数据"
            )
        
        # 调用AI分析
        analysis_result = await llm_analyzer.analyze_questionnaire(
            stats=stats,
            session_id=session_id,
            use_simple_prompt=use_simple_prompt
        )
        
        if not analysis_result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=f"AI分析失败: {analysis_result.get('error')}"
            )
        
        # 保存分析结果到数据库
        try:
            db.save_analysis_result(
                session_id=session_id,
                analysis_text=analysis_result['analysis_text'],  # 保存原始JSON文本
                model_name=analysis_result['model'],
                total_responses=analysis_result['total_responses']
            )
        except Exception as e:
            print(f"⚠️  保存分析结果失败: {e}")
            # 不影响返回，继续
        
        return {
            "success": True,
            "data": analysis_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )


@app.get("/api/analyze/{session_id}")
async def get_analysis_result(session_id: str):
    """
    获取已保存的AI分析结果
    
    返回:
    {
        "success": true,
        "data": {
            "session_id": "...",
            "analysis": "...",
            "model": "...",
            "total_responses": 20,
            "analyzed_at": "2024-01-01T12:00:00"
        }
    }
    """
    try:
        result = db.get_analysis_result(session_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"未找到会话 {session_id} 的分析结果"
            )
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取分析结果失败: {str(e)}"
        )


@app.get("/api/models")
async def get_available_models():
    """
    获取可用的AI模型列表
    
    返回:
    {
        "success": true,
        "data": [
            {
                "id": "anthropic/claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "provider": "Anthropic",
                "description": "...",
                "recommended": true
            },
            ...
        ]
    }
    """
    try:
        if llm_analyzer is None:
            return {
                "success": False,
                "error": "AI分析功能未配置"
            }
        
        models = llm_analyzer.get_available_models()
        
        return {
            "success": True,
            "data": models
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取模型列表失败: {str(e)}"
        )


# ================================================================
# 错误处理
# ================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "服务器内部错误",
            "detail": str(exc)
        }
    )


# ================================================================
# 启动命令
# ================================================================
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )

