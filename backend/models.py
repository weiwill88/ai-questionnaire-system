"""
数据模型定义
使用Pydantic进行数据验证
"""
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class QuestionnaireSubmit(BaseModel):
    """问卷提交数据模型"""
    
    # 场次ID
    session_id: str = Field(..., description="场次标识")
    
    # Q1: 机构类型
    q1_industry: str = Field(..., description="机构类型")
    q1_industry_other: Optional[str] = Field(None, description="机构类型-其他")
    
    # Q2: 工作方向
    q2_role: str = Field(..., description="工作方向")
    q2_role_other: Optional[str] = Field(None, description="工作方向-其他")
    
    # Q3-Q7, Q9: 单选题（整数）
    q3_digital_habit: int = Field(..., ge=1, le=4, description="数字工具习惯")
    q4_ai_self_position: int = Field(..., ge=1, le=4, description="AI应用自我定位")
    q5_ai_usage: int = Field(..., ge=1, le=5, description="AI工具使用情况")
    q6_org_stage: int = Field(..., ge=1, le=5, description="机构AI阶段")
    q7_personal_role: int = Field(..., ge=1, le=4, description="个人项目角色")
    q9_attitude: int = Field(..., ge=1, le=5, description="对AI的态度")
    
    # Q8: 痛点场景（多选，数组）
    q8_pain_points: List[str] = Field(..., description="痛点场景")
    
    # Q10: 推进约束（可选多选）
    q10_constraints: Optional[List[str]] = Field(None, description="推进约束")
    
    # 元数据
    completion_time_seconds: Optional[int] = Field(None, description="填写耗时（秒）")
    device_type: str = Field(default="unknown", description="设备类型")
    user_agent: Optional[str] = Field(None, description="浏览器UA")
    ip_hash: Optional[str] = Field(None, description="IP/指纹哈希")
    
    @validator('q8_pain_points')
    def validate_pain_points(cls, v):
        """验证Q8至少选1项，最多3项"""
        if not v or len(v) == 0:
            raise ValueError('Q8至少需要选择1项')
        if len(v) > 3:
            raise ValueError('Q8最多只能选择3项')
        return v
    
    @validator('q10_constraints')
    def validate_constraints(cls, v):
        """验证Q10最多3项"""
        if v and len(v) > 3:
            raise ValueError('Q10最多只能选择3项')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "SJTU_SAIF_20251114",
                "q1_industry": "bank",
                "q1_industry_other": None,
                "q2_role": "investment",
                "q2_role_other": None,
                "q3_digital_habit": 3,
                "q4_ai_self_position": 2,
                "q5_ai_usage": 3,
                "q6_org_stage": 2,
                "q7_personal_role": 2,
                "q8_pain_points": ["research_reading", "doc_writing"],
                "q9_attitude": 2,
                "q10_constraints": ["data_security"],
                "completion_time_seconds": 138,
                "device_type": "mobile",
                "user_agent": "Mozilla/5.0...",
                "ip_hash": "5d41402abc4b..."
            }
        }


class SubmitResponse(BaseModel):
    """提交成功响应"""
    success: bool = True
    message: str = "提交成功"
    id: str = Field(..., description="响应ID")


class StatsResponse(BaseModel):
    """统计数据响应"""
    session_id: str
    total_responses: int
    avg_completion_seconds: Optional[int] = None
    latest_submission: Optional[dict] = None
    industry_distribution: Optional[dict] = None
    role_distribution: Optional[dict] = None
    attitude_distribution: Optional[dict] = None
    pain_points_stats: Optional[dict] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    detail: Optional[str] = None

