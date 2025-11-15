"""
AI分析提示词模板 - 输出JSON结构
"""

ANALYSIS_SYSTEM_PROMPT = """你是一位资深的金融行业AI应用专家和数据分析师。你的任务是分析MBA学生的问卷调研结果，并为演讲者提供针对性的内容建议。

**重要**：你必须输出严格的JSON格式，不要有任何额外的文字说明。"""

# 问卷题目说明（用于AI理解评分）
QUESTION_LABELS = {
    'q3_digital_habit': {
        1: '基础工具（Office等）',
        2: 'Excel高级+简单BI',
        3: 'SQL查询/Python脚本',
        4: '搭建工具/自动化流程'
    },
    'q4_ai_self_position': {
        1: '好奇观望',
        2: '个人用户',
        3: '场景探索',
        4: '推动落地'
    },
    'q5_ai_usage': {
        1: '还没怎么用过',
        2: '偶尔用（查资料、文案）',
        3: '经常用（有固定模板）',
        4: '深度用（分析、方案设计）',
        5: '团队推广（培训、规范）'
    },
    'q6_org_stage': {
        1: '调研讨论阶段',
        2: '小范围试点',
        3: '多场景稳定使用',
        4: '整体规划推进',
        5: '不确定'
    },
    'q7_personal_role': {
        1: '使用者',
        2: '参与者',
        3: '推动者',
        4: '观察者'
    },
    'q9_attitude': {
        1: '积极拥抱',
        2: '理性谨慎',
        3: '观望等待',
        4: '存疑担忧',
        5: '不确定'
    }
}

def _format_stats_for_prompt(stats: dict) -> str:
    """格式化统计数据用于提示词"""
    
    def format_dist(data: dict, labels: dict = None) -> str:
        if not data:
            return "（无数据）"
        total = sum(data.values())
        lines = []
        for key, count in sorted(data.items(), key=lambda x: x[1], reverse=True):
            pct = count / total * 100
            label = labels.get(int(key) if key.isdigit() else key, key) if labels else key
            lines.append(f"  - {label}: {count}人 ({pct:.1f}%)")
        return "\n".join(lines)
    
    return f"""
# 受众数据概览
- 总样本: {stats.get('total_responses', 0)}人
- 平均完成时间: {stats.get('avg_completion_time', 0):.1f}秒

## 行业分布
{format_dist(stats.get('industries', {}))}

## 职位角色
{format_dist(stats.get('roles', {}))}

## 数字化能力（Q3）
{format_dist(stats.get('digital_habits', {}), QUESTION_LABELS['q3_digital_habit'])}

## AI认知定位（Q4）
{format_dist(stats.get('ai_self_positions', {}), QUESTION_LABELS['q4_ai_self_position'])}

## AI使用程度（Q5）
{format_dist(stats.get('ai_usages', {}), QUESTION_LABELS['q5_ai_usage'])}

## 机构AI阶段（Q6）
{format_dist(stats.get('org_stages', {}), QUESTION_LABELS['q6_org_stage'])}

## 个人项目角色（Q7）
{format_dist(stats.get('personal_roles', {}), QUESTION_LABELS['q7_personal_role'])}

## 主要痛点（Q8）
{format_dist(stats.get('pain_points', {}))}

## 对AI态度（Q9）
{format_dist(stats.get('attitudes', {}), QUESTION_LABELS['q9_attitude'])}

## 推进约束（Q10）
{format_dist(stats.get('constraints', {}))}
"""

def get_analysis_prompt(stats: dict) -> str:
    """生成完整的分析提示词"""
    
    stats_text = _format_stats_for_prompt(stats)
    
    prompt = f"""{stats_text}

---

# 演讲内容设计

**课程背景**: 上海交通大学高级金融学院MBA课程
**总时长**: 2小时
**目标**: 大模型应用实战分享

## 第一小时：内容讲解

### Part 1: 概念与趋势（30分钟）
- 大模型过去3年的发展历程
- 当前市场观察与趋势分析


### Part 2: 案例演示（30分钟）

**案例1: 智能简历筛选**
- 技术栈: LlamaIndex
- 场景: 简历问答 + 智能筛选
- 痛点: HR效率、候选人匹配度

**案例2: 合同审查工作流**
- 技术栈: Dify
- 场景: 多节点工作流
- 痛点: 合规审查、风险识别

**案例3: 信贷尽调报告生成**
- 技术栈: 多Agent系统（二次开发开源框架）
- 场景: 信贷尽调报告自动化
- 痛点: 研究效率、信息整合

**灵活案例: 制造业授权报价Agent**
- 场景: B2B报价流程自动化
- 可根据现场反馈决定是否演示

## 第二小时：交流讨论
- Q&A环节
- 可能的现场PoC演示
- 经验交流

---

# 分析任务

请基于以上问卷数据和演讲设计，输出以下JSON结构的分析报告：

```json
{{
  "audience_analysis": {{
    "summary": "100-150字的受众整体画像",
    "key_characteristics": [
      {{"dimension": "行业背景", "insight": "简要洞察", "percentage": "关键数据"}},
      {{"dimension": "数字化水平", "insight": "简要洞察", "percentage": "关键数据"}},
      {{"dimension": "AI成熟度", "insight": "简要洞察", "percentage": "关键数据"}}
    ],
    "readiness_score": {{
      "technical": {{"score": 0-10, "description": "技术准备度描述"}},
      "mindset": {{"score": 0-10, "description": "认知态度描述"}},
      "organizational": {{"score": 0-10, "description": "组织支持度描述"}}
    }}
  }},
  
  "key_findings": [
    {{
      "title": "关键发现标题",
      "priority": "high/medium/low",
      "details": ["具体观察点1", "具体观察点2"],
      "implication": "对演讲的影响"
    }}
  ],
  
  "content_recommendations": {{
    "part1_concepts": {{
      "emphasis": ["应该强调的概念1", "应该强调的概念2", "应该强调的概念3"],
      "depth_level": "入门/进阶/深度",
      "suggested_topics": [
        {{"topic": "话题", "rationale": "为什么讲这个", "time_allocation": "5-10分钟"}}
      ],
      "avoid": ["应该避免或轻描淡写的话题"]
    }},
    
    "part2_cases": {{
      "case1_resume": {{
        "relevance_score": 0-10,
        "emphasis": ["应该重点展示什么", "受众关心什么"],
        "demo_suggestions": "演示建议",
        "qa_predictions": ["可能被问的问题"]
      }},
      "case2_contract": {{
        "relevance_score": 0-10,
        "emphasis": ["应该重点展示什么"],
        "demo_suggestions": "演示建议",
        "qa_predictions": ["可能被问的问题"]
      }},
      "case3_research": {{
        "relevance_score": 0-10,
        "emphasis": ["应该重点展示什么"],
        "demo_suggestions": "演示建议",
        "qa_predictions": ["可能被问的问题"]
      }},
      "case_order_suggestion": {{
        "recommended_order": [1, 2, 3],
        "rationale": "为什么建议这个顺序"
      }},
      "flexible_case": {{
        "should_present": true/false,
        "rationale": "是否演示制造业案例的理由"
      }}
    }},
    
    "time_allocation": {{
      "part1_breakdown": {{"development": "X分钟", "trends": "X分钟", "finance_status": "X分钟"}},
      "part2_breakdown": {{"case1": "X分钟", "case2": "X分钟", "case3": "X分钟"}},
      "adjustment_rationale": "时间分配的理由"
    }}
  }},
  
  "interaction_design": {{
    "live_poc_suggestions": [
      {{
        "scenario": "现场演示场景",
        "description": "具体做什么",
        "why": "为什么受众会感兴趣",
        "preparation": "需要什么准备",
        "time_needed": "预计时间"
      }}
    ],
    "qa_strategy": {{
      "predicted_questions": [
        {{"question": "预测的问题", "suggested_answer": "建议回答要点"}}
      ],
      "difficult_topics": ["可能有争议的话题", "应对策略"]
    }},
    "discussion_topics": [
      {{"topic": "讨论话题", "starter": "如何引入", "expected_outcome": "期望达到的效果"}}
    ]
  }},
  
  "audience_segments": [
    {{
      "segment_name": "群体名称",
      "percentage": 30,
      "count": 6,
      "characteristics": "群体特征",
      "pain_points": ["痛点1", "痛点2"],
      "engagement_strategy": "如何吸引这个群体"
    }}
  ],
  
  "practical_tips": {{
    "opening": "开场建议（如何破冰、如何引起兴趣）",
    "transitions": "案例间过渡建议",
    "engagement_techniques": ["保持互动的技巧"],
    "closing": "收尾建议（如何总结、如何引导后续）"
  }}
}}
```

**要求**：
1. 输出必须是有效的JSON格式
2. 所有字段都必须填写
3. 数据要基于问卷实际情况
4. 建议要具体、可操作
5. 考虑金融MBA学生的特点
6. 重点关注如何让演讲更有针对性和互动性
"""
    
    return prompt


# 简化版提示词（如果需要快速分析）
def get_simple_analysis_prompt(stats: dict) -> str:
    """生成简化版提示词"""
    
    stats_text = _format_stats_for_prompt(stats)
    
    prompt = f"""{stats_text}

请基于以上数据，为一场2小时的AI应用演讲（1小时讲解+1小时讨论）提供简要建议。

输出JSON格式：
{{
  "audience_summary": "受众特点总结（100字）",
  "top_3_insights": ["洞察1", "洞察2", "洞察3"],
  "content_focus": ["应该重点讲的3个方面"],
  "case_priority": ["案例1优先级评分", "案例2优先级评分", "案例3优先级评分"],
  "interaction_tips": ["互动建议1", "互动建议2"]
}}
"""
    
    return prompt
