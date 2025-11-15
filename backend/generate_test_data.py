#!/usr/bin/env python3
"""
生成测试问卷数据并提交到Supabase
匹配前端questionnaire.html的实际字段结构
"""
import random
import hashlib
import asyncio
from database import db

# 问卷选项定义（匹配前端）
Q1_INDUSTRIES = [
    "银行（含政策性银行、商业银行）",
    "证券公司",
    "基金公司（公募 / 私募 / 资管）",
    "期货公司",
    "保险公司",
    "信托公司",
    "其他持牌金融机构（如消费金融、金融租赁、金控集团等）",
    "金融科技公司（非持牌）"
]

Q2_ROLES = [
    "对公 / 公司金融业务",
    "对私 / 零售 / 财富管理",
    "投研 / 交易 / 资产管理",
    "风险管理 / 合规 / 内控",
    "运营 / 清结算 / 托管",
    "科技 / 数据 / IT",
    "产品开发 / 创新",
    "战略 / 规划 / 综合管理"
]

Q8_PAIN_POINTS = [
    "数据质量和标准化问题",
    "模型可解释性和信任度不足",
    "技术落地和产品化困难",
    "缺乏专业人才",
    "监管合规和风险管理挑战",
    "与现有系统集成复杂",
    "投入产出比不明确",
    "内部认知和推动阻力",
    "供应商选择和评估困难"
]

Q10_CONSTRAINTS = [
    "预算和成本约束",
    "监管政策限制",
    "数据安全和隐私要求",
    "组织架构和流程限制",
    "技术基础设施不足",
    "人才短缺",
    "业务部门配合度低",
    "高层支持不足"
]

def generate_random_response():
    """生成一条随机的问卷响应"""
    
    # 随机选择是否填写"其他"选项
    use_industry_other = random.random() < 0.1  # 10%概率填写其他
    use_role_other = random.random() < 0.1
    
    if use_industry_other:
        q1_industry = "其他行业"
        q1_industry_other = random.choice([
            "金融监管机构",
            "金融咨询公司",
            "金融研究机构",
            "互联网金融平台",
            "高校金融研究"
        ])
    else:
        q1_industry = random.choice(Q1_INDUSTRIES)
        q1_industry_other = None
    
    if use_role_other:
        q2_role = "其他"
        q2_role_other = random.choice([
            "数据分析师",
            "产品经理",
            "合规专员",
            "研究员",
            "项目经理"
        ])
    else:
        q2_role = random.choice(Q2_ROLES)
        q2_role_other = None
    
    # Q3-Q7, Q9 是评分题（1-5或1-4）
    # 使用正态分布，让结果更真实（偏向中间值）
    def random_rating(min_val, max_val):
        """生成偏向中间值的随机评分"""
        mean = (min_val + max_val) / 2
        std = (max_val - min_val) / 4
        value = int(random.gauss(mean, std))
        return max(min_val, min(max_val, value))
    
    q3_digital_habit = random_rating(1, 4)
    q4_ai_self_position = random_rating(1, 4)
    q5_ai_usage = random_rating(1, 5)
    q6_org_stage = random_rating(1, 5)
    q7_personal_role = random_rating(1, 4)
    q9_attitude = random_rating(1, 5)
    
    # Q8 痛点场景（多选，1-3项）
    q8_pain_points = random.sample(Q8_PAIN_POINTS, k=random.randint(1, 3))
    
    # Q10 推进约束（多选，可选，90%的人会填）
    if random.random() < 0.9:
        q10_constraints = random.sample(Q10_CONSTRAINTS, k=random.randint(1, 3))
    else:
        q10_constraints = None
    
    # 生成唯一的ip_hash
    ip_hash = hashlib.sha256(f"test_{random.randint(1, 1000000)}_{random.random()}".encode()).hexdigest()
    
    # 随机设备类型
    device_type = random.choice(['mobile', 'mobile', 'mobile', 'desktop'])  # 75%移动端
    
    # 随机完成时间（60-300秒）
    completion_time_seconds = random.randint(60, 300)
    
    # 生成随机User-Agent
    user_agents = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
        'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ]
    
    return {
        'session_id': 'SJTU_SAIF_20251114',
        'q1_industry': q1_industry,
        'q1_industry_other': q1_industry_other,
        'q2_role': q2_role,
        'q2_role_other': q2_role_other,
        'q3_digital_habit': q3_digital_habit,
        'q4_ai_self_position': q4_ai_self_position,
        'q5_ai_usage': q5_ai_usage,
        'q6_org_stage': q6_org_stage,
        'q7_personal_role': q7_personal_role,
        'q8_pain_points': q8_pain_points,  # PostgreSQL数组
        'q9_attitude': q9_attitude,
        'q10_constraints': q10_constraints,  # PostgreSQL数组或null
        'ip_hash': ip_hash,
        'device_type': device_type,
        'completion_time_seconds': completion_time_seconds,
        'user_agent': random.choice(user_agents)
    }

async def main():
    """生成并插入测试数据"""
    print("🎲 开始生成测试数据...")
    print("📋 使用前端HTML匹配的字段结构（整数评分 + 文本数组）")
    
    num_responses = 20
    successful = 0
    failed = 0
    
    for i in range(num_responses):
        try:
            response = generate_random_response()
            
            # 插入数据库
            result = db.client.table('responses').insert(response).execute()
            
            successful += 1
            print(f"✅ [{successful}/{num_responses}] 已生成测试数据")
            
        except Exception as e:
            failed += 1
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            print(f"❌ 生成第 {i+1} 条数据时出错: {error_msg}")
    
    print(f"\n{'='*60}")
    print(f"🎉 完成! 成功: {successful}/{num_responses}, 失败: {failed}/{num_responses}")
    print(f"📊 Session ID: SJTU_SAIF_20251114")
    print(f"{'='*60}")
    
    # 显示统计
    if successful > 0:
        try:
            stats = await db.get_statistics('SJTU_SAIF_20251114')
            print(f"\n📈 当前统计:")
            print(f"   总提交数: {stats.get('total_responses', 0)}")
            print(f"   平均完成时间: {stats.get('avg_completion_time', 0):.1f}秒")
            
            # 显示行业分布
            industries = stats.get('industries', {})
            if industries:
                print(f"\n🏢 行业分布（Top 5）:")
                sorted_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]
                for industry, count in sorted_industries:
                    print(f"   - {industry}: {count}人")
            
            # 显示痛点分布
            pain_points = stats.get('pain_points', {})
            if pain_points:
                print(f"\n⚠️  主要痛点（Top 5）:")
                sorted_pain_points = sorted(pain_points.items(), key=lambda x: x[1], reverse=True)[:5]
                for pain_point, count in sorted_pain_points:
                    print(f"   - {pain_point}: {count}次提及")
            
        except Exception as e:
            print(f"⚠️  无法获取统计信息: {e}")

if __name__ == '__main__':
    asyncio.run(main())
