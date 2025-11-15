"""
Supabase数据库操作封装
"""
import os
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Database:
    """数据库操作类"""
    
    def __init__(self):
        """初始化Supabase客户端"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')  # 使用service_role key
        
        if not supabase_url or not supabase_key:
            raise ValueError("缺少SUPABASE_URL或SUPABASE_SERVICE_KEY环境变量")
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    async def insert_response(self, data: Dict[str, Any]) -> str:
        """
        插入问卷回答
        
        Args:
            data: 问卷数据字典
            
        Returns:
            响应ID (UUID)
            
        Raises:
            Exception: 插入失败时抛出异常
        """
        try:
            result = self.client.table('responses').insert(data).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]['id']
            else:
                raise Exception("插入失败，未返回数据")
                
        except Exception as e:
            # 检查是否是重复提交错误
            if 'unique_submission_per_ip' in str(e):
                raise Exception("您已经提交过问卷，请勿重复提交")
            raise Exception(f"数据库插入失败: {str(e)}")
    
    async def get_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        获取问卷统计数据
        
        Args:
            session_id: 场次ID
            
        Returns:
            统计数据字典
        """
        try:
            # 调用数据库函数获取统计
            result = self.client.rpc(
                'get_session_statistics',
                {'p_session_id': session_id}
            ).execute()
            
            if result.data:
                stats = result.data
                
                # 获取最新提交时间
                latest = self.client.table('responses')\
                    .select('created_at')\
                    .eq('session_id', session_id)\
                    .order('created_at', desc=True)\
                    .limit(1)\
                    .execute()
                
                if latest.data and len(latest.data) > 0:
                    from datetime import datetime, timezone
                    latest_time = datetime.fromisoformat(
                        latest.data[0]['created_at'].replace('Z', '+00:00')
                    )
                    now = datetime.now(timezone.utc)
                    seconds_ago = int((now - latest_time).total_seconds())
                    
                    stats['latest_submission'] = {
                        'created_at': latest.data[0]['created_at'],
                        'seconds_ago': seconds_ago
                    }
                else:
                    stats['latest_submission'] = None
                
                return stats
            
            # 如果函数返回空，手动查询
            return await self._manual_statistics(session_id)
            
        except Exception as e:
            print(f"获取统计失败: {str(e)}")
            # 降级到手动查询
            return await self._manual_statistics(session_id)
    
    async def _manual_statistics(self, session_id: str) -> Dict[str, Any]:
        """手动统计（备用方案）"""
        try:
            # 查询所有回答
            responses = self.client.table('responses')\
                .select('*')\
                .eq('session_id', session_id)\
                .execute()
            
            if not responses.data:
                return {
                    'session_id': session_id,
                    'total_responses': 0,
                    'avg_completion_seconds': None,
                    'latest_submission': None,
                    'industry_distribution': {},
                    'role_distribution': {},
                    'attitude_distribution': {},
                    'pain_points_stats': {}
                }
            
            data = responses.data
            total = len(data)
            
            # 计算平均时间
            times = [r['completion_time_seconds'] for r in data if r.get('completion_time_seconds')]
            avg_time = int(sum(times) / len(times)) if times else None
            
            # 统计分布
            industry_dist = {}
            role_dist = {}
            attitude_dist = {}
            pain_points_count = {}
            
            for r in data:
                # 行业分布
                ind = r.get('q1_industry')
                if ind:
                    industry_dist[ind] = industry_dist.get(ind, 0) + 1
                
                # 岗位分布
                role = r.get('q2_role')
                if role:
                    role_dist[role] = role_dist.get(role, 0) + 1
                
                # 态度分布
                att = str(r.get('q9_attitude'))
                if att:
                    attitude_dist[att] = attitude_dist.get(att, 0) + 1
                
                # 痛点统计
                if r.get('q8_pain_points'):
                    for pain in r['q8_pain_points']:
                        pain_points_count[pain] = pain_points_count.get(pain, 0) + 1
            
            # 最新提交
            latest = sorted(data, key=lambda x: x['created_at'], reverse=True)[0]
            from datetime import datetime, timezone
            latest_time = datetime.fromisoformat(
                latest['created_at'].replace('Z', '+00:00')
            )
            now = datetime.now(timezone.utc)
            seconds_ago = int((now - latest_time).total_seconds())
            
            return {
                'session_id': session_id,
                'total_responses': total,
                'avg_completion_seconds': avg_time,
                'latest_submission': {
                    'created_at': latest['created_at'],
                    'seconds_ago': seconds_ago
                },
                'industry_distribution': industry_dist,
                'role_distribution': role_dist,
                'attitude_distribution': attitude_dist,
                'pain_points_stats': pain_points_count
            }
            
        except Exception as e:
            raise Exception(f"手动统计失败: {str(e)}")
    
    async def get_all_responses(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取所有问卷回答
        
        Args:
            session_id: 场次ID
            
        Returns:
            问卷回答列表
        """
        try:
            result = self.client.table('responses')\
                .select('*')\
                .eq('session_id', session_id)\
                .order('created_at', desc=True)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            raise Exception(f"查询失败: {str(e)}")
    
    def save_analysis_result(
        self, 
        session_id: str, 
        analysis_text: str,
        model_name: str,
        total_responses: int
    ) -> Dict[str, Any]:
        """
        保存AI分析结果到数据库
        
        Args:
            session_id: 会话ID
            analysis_text: 分析文本
            model_name: 使用的模型名称
            total_responses: 分析的问卷数量
        
        Returns:
            保存的记录
        """
        try:
            data = {
                'session_id': session_id,
                'analysis_text': analysis_text,
                'model_name': model_name,
                'total_responses': total_responses
            }
            
            result = self.client.table('analysis_results')\
                .upsert(data, on_conflict='session_id')\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            raise Exception(f"保存分析结果失败: {str(e)}")
    
    def get_analysis_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取已保存的AI分析结果
        
        Args:
            session_id: 会话ID
        
        Returns:
            分析结果或None
        """
        try:
            result = self.client.table('analysis_results')\
                .select('*')\
                .eq('session_id', session_id)\
                .single()\
                .execute()
            
            if result.data:
                return {
                    'session_id': result.data['session_id'],
                    'analysis': result.data['analysis_text'],
                    'model': result.data['model_name'],
                    'total_responses': result.data['total_responses'],
                    'analyzed_at': result.data['created_at']
                }
            
            return None
            
        except Exception as e:
            # 如果找不到记录，返回None而不是抛出异常
            if "404" in str(e) or "No rows" in str(e):
                return None
            raise Exception(f"获取分析结果失败: {str(e)}")


# 全局数据库实例
db = Database()

