-- ================================================================
-- AI应用需求调研系统 - 数据库初始化脚本
-- 匹配前端questionnaire.html的实际字段结构
-- ================================================================

-- 清理旧表（如果需要重新创建）
-- DROP TABLE IF EXISTS analysis_results CASCADE;
-- DROP TABLE IF EXISTS responses CASCADE;
-- DROP TABLE IF EXISTS sessions CASCADE;

-- ----------------------------------------------------------------
-- 1. 问卷响应表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS responses (
  -- 主键与元数据
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id VARCHAR(50) NOT NULL DEFAULT 'SJTU_SAIF_20251114',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Q1: 机构类型（单选）
  q1_industry VARCHAR(100) NOT NULL,
  q1_industry_other VARCHAR(200),
  
  -- Q2: 工作方向（单选）
  q2_role VARCHAR(100) NOT NULL,
  q2_role_other VARCHAR(200),
  
  -- Q3: 数字工具习惯（单选，1-4）
  q3_digital_habit INTEGER NOT NULL CHECK (q3_digital_habit BETWEEN 1 AND 4),
  
  -- Q4: AI应用自我定位（单选，1-4）
  q4_ai_self_position INTEGER NOT NULL CHECK (q4_ai_self_position BETWEEN 1 AND 4),
  
  -- Q5: AI工具使用情况（单选，1-5）
  q5_ai_usage INTEGER NOT NULL CHECK (q5_ai_usage BETWEEN 1 AND 5),
  
  -- Q6: 机构AI阶段（单选，1-5）
  q6_org_stage INTEGER NOT NULL CHECK (q6_org_stage BETWEEN 1 AND 5),
  
  -- Q7: 个人项目角色（单选，1-4）
  q7_personal_role INTEGER NOT NULL CHECK (q7_personal_role BETWEEN 1 AND 4),
  
  -- Q8: 痛点场景（多选，PostgreSQL文本数组）
  q8_pain_points TEXT[] NOT NULL,
  
  -- Q9: 对AI的态度（单选，1-5）
  q9_attitude INTEGER NOT NULL CHECK (q9_attitude BETWEEN 1 AND 5),
  
  -- Q10: 推进约束（多选，可选，PostgreSQL文本数组）
  q10_constraints TEXT[],
  
  -- 提交元数据
  completion_time_seconds INTEGER,
  user_agent TEXT,
  ip_hash VARCHAR(64),
  device_type VARCHAR(20) DEFAULT 'unknown',
  
  -- 约束
  CONSTRAINT unique_ip_session UNIQUE(ip_hash, session_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_responses_session ON responses(session_id);
CREATE INDEX IF NOT EXISTS idx_responses_created ON responses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_responses_industry ON responses(q1_industry);
CREATE INDEX IF NOT EXISTS idx_responses_role ON responses(q2_role);
CREATE INDEX IF NOT EXISTS idx_responses_ip_hash ON responses(ip_hash);

-- 添加注释
COMMENT ON TABLE responses IS '问卷响应表';
COMMENT ON COLUMN responses.q1_industry IS 'Q1: 机构类型';
COMMENT ON COLUMN responses.q2_role IS 'Q2: 工作方向';
COMMENT ON COLUMN responses.q3_digital_habit IS 'Q3: 数字工具习惯（1-4）';
COMMENT ON COLUMN responses.q4_ai_self_position IS 'Q4: AI应用自我定位（1-4）';
COMMENT ON COLUMN responses.q5_ai_usage IS 'Q5: AI工具使用情况（1-5）';
COMMENT ON COLUMN responses.q6_org_stage IS 'Q6: 机构AI阶段（1-5）';
COMMENT ON COLUMN responses.q7_personal_role IS 'Q7: 个人项目角色（1-4）';
COMMENT ON COLUMN responses.q8_pain_points IS 'Q8: 痛点场景（多选，文本数组）';
COMMENT ON COLUMN responses.q9_attitude IS 'Q9: 对AI的态度（1-5）';
COMMENT ON COLUMN responses.q10_constraints IS 'Q10: 推进约束（多选，可选，文本数组）';

-- ----------------------------------------------------------------
-- 2. AI分析结果表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analysis_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id VARCHAR(50) NOT NULL UNIQUE,
  analysis_text TEXT NOT NULL,
  model_name VARCHAR(100) NOT NULL,
  total_responses INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analysis_session ON analysis_results(session_id);

COMMENT ON TABLE analysis_results IS 'AI分析结果表';
COMMENT ON COLUMN analysis_results.analysis_text IS 'AI分析文本（Markdown格式）';
COMMENT ON COLUMN analysis_results.model_name IS '使用的AI模型名称';

-- ----------------------------------------------------------------
-- 3. 会话管理表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
  session_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(200),
  description TEXT,
  start_time TIMESTAMPTZ,
  end_time TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE sessions IS '会话管理表，用于管理不同批次的问卷';

-- 插入默认会话
INSERT INTO sessions (session_id, name, description, start_time, is_active)
VALUES ('SJTU_SAIF_20251114', '上海交大高金MBA课程', 'AI应用需求调研', NOW(), true)
ON CONFLICT (session_id) DO NOTHING;

-- ----------------------------------------------------------------
-- 4. 实时统计视图
-- ----------------------------------------------------------------
CREATE OR REPLACE VIEW session_stats AS
SELECT 
  session_id,
  COUNT(*) as total_responses,
  AVG(completion_time_seconds) as avg_completion_time,
  COUNT(CASE WHEN device_type = 'mobile' THEN 1 END) as mobile_count,
  COUNT(CASE WHEN device_type = 'desktop' THEN 1 END) as desktop_count,
  MIN(created_at) as first_response_time,
  MAX(created_at) as last_response_time
FROM responses
GROUP BY session_id;

COMMENT ON VIEW session_stats IS '会话统计视图';

-- ----------------------------------------------------------------
-- 5. 获取统计数据的函数
-- ----------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_session_statistics(p_session_id VARCHAR)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'total_responses', COUNT(*),
    'avg_completion_time', ROUND(AVG(completion_time_seconds)::numeric, 1),
    'mobile_count', COUNT(CASE WHEN device_type = 'mobile' THEN 1 END),
    'desktop_count', COUNT(CASE WHEN device_type = 'desktop' THEN 1 END),
    
    -- Q1行业分布
    'industries', (
      SELECT json_object_agg(COALESCE(q1_industry, 'unknown'), cnt)
      FROM (
        SELECT q1_industry, COUNT(*) as cnt
        FROM responses
        WHERE session_id = p_session_id
        GROUP BY q1_industry
      ) sub
    ),
    
    -- Q2角色分布
    'roles', (
      SELECT json_object_agg(COALESCE(q2_role, 'unknown'), cnt)
      FROM (
        SELECT q2_role, COUNT(*) as cnt
        FROM responses
        WHERE session_id = p_session_id
        GROUP BY q2_role
      ) sub
    ),
    
    -- Q3 数字工具习惯分布
    'digital_habits', (
      SELECT json_object_agg(q3_digital_habit::text, cnt)
      FROM (
        SELECT q3_digital_habit, COUNT(*) as cnt
        FROM responses
        WHERE session_id = p_session_id
        GROUP BY q3_digital_habit
        ORDER BY q3_digital_habit
      ) sub
    ),
    
    -- Q4 AI自我定位分布
    'ai_self_positions', (
      SELECT json_object_agg(q4_ai_self_position::text, cnt)
      FROM (
        SELECT q4_ai_self_position, COUNT(*) as cnt
        FROM responses
        WHERE session_id = p_session_id
        GROUP BY q4_ai_self_position
        ORDER BY q4_ai_self_position
      ) sub
    ),
    
    -- Q5 AI使用情况分布
    'ai_usages', (
      SELECT json_object_agg(q5_ai_usage::text, cnt)
      FROM (
        SELECT q5_ai_usage, COUNT(*) as cnt
        FROM responses
        WHERE session_id = p_session_id
        GROUP BY q5_ai_usage
        ORDER BY q5_ai_usage
      ) sub
    ),
    
    -- Q6 机构AI阶段分布
    'org_stages', (
      SELECT json_object_agg(q6_org_stage::text, cnt)
      FROM (
        SELECT q6_org_stage, COUNT(*) as cnt
        FROM responses
        WHERE session_id = p_session_id
        GROUP BY q6_org_stage
        ORDER BY q6_org_stage
      ) sub
    ),
    
    -- Q7 个人项目角色分布
    'personal_roles', (
      SELECT json_object_agg(q7_personal_role::text, cnt)
      FROM (
        SELECT q7_personal_role, COUNT(*) as cnt
        FROM responses
        WHERE session_id = p_session_id
        GROUP BY q7_personal_role
        ORDER BY q7_personal_role
      ) sub
    ),
    
    -- Q8 痛点场景统计（展开数组）
    'pain_points', (
      SELECT json_object_agg(pain_point, cnt)
      FROM (
        SELECT unnest(q8_pain_points) as pain_point, COUNT(*) as cnt
        FROM responses
        WHERE session_id = p_session_id
        GROUP BY pain_point
      ) sub
    ),
    
    -- Q9 对AI态度分布
    'attitudes', (
      SELECT json_object_agg(q9_attitude::text, cnt)
      FROM (
        SELECT q9_attitude, COUNT(*) as cnt
        FROM responses
        WHERE session_id = p_session_id
        GROUP BY q9_attitude
        ORDER BY q9_attitude
      ) sub
    ),
    
    -- Q10 推进约束统计（展开数组，可能为null）
    'constraints', (
      SELECT json_object_agg(constraint_item, cnt)
      FROM (
        SELECT unnest(q10_constraints) as constraint_item, COUNT(*) as cnt
        FROM responses
        WHERE session_id = p_session_id AND q10_constraints IS NOT NULL
        GROUP BY constraint_item
      ) sub
    )
    
  ) INTO result
  FROM responses
  WHERE session_id = p_session_id;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_session_statistics IS '获取指定会话的统计数据';

-- ----------------------------------------------------------------
-- 6. 清理函数
-- ----------------------------------------------------------------

CREATE OR REPLACE FUNCTION cleanup_session(p_session_id VARCHAR)
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM analysis_results WHERE session_id = p_session_id;
  
  WITH deleted AS (
    DELETE FROM responses WHERE session_id = p_session_id
    RETURNING *
  )
  SELECT COUNT(*) INTO deleted_count FROM deleted;
  
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_session IS '清理指定会话的所有数据';

-- ----------------------------------------------------------------
-- 7. 启用Row Level Security
-- ----------------------------------------------------------------

ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- 允许匿名用户插入responses
CREATE POLICY "Allow anonymous insert" ON responses
  FOR INSERT TO anon
  WITH CHECK (true);

-- 允许service_role访问所有数据
CREATE POLICY "Allow service role all" ON responses
  FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow service role all analysis" ON analysis_results
  FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow service role all sessions" ON sessions
  FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

-- ----------------------------------------------------------------
-- 8. 启用Realtime
-- ----------------------------------------------------------------

ALTER PUBLICATION supabase_realtime ADD TABLE responses;
ALTER PUBLICATION supabase_realtime ADD TABLE analysis_results;

-- ================================================================
-- 完成
-- ================================================================

-- 验证表结构
SELECT 
  table_name,
  (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
  AND table_name IN ('responses', 'analysis_results', 'sessions')
ORDER BY table_name;

-- 显示成功消息
DO $$
BEGIN
  RAISE NOTICE '✅ 数据库初始化完成！';
  RAISE NOTICE '📊 已创建表: responses (匹配前端HTML字段), analysis_results, sessions';
  RAISE NOTICE '🔍 已创建视图: session_stats';
  RAISE NOTICE '⚡ 已启用Realtime订阅';
  RAISE NOTICE '🔐 已配置Row Level Security';
END $$;
