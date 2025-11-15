"""
LLM分析器 - 通过OpenRouter调用大模型进行问卷分析
"""
import os
import httpx
from typing import Dict, Optional
from prompts import ANALYSIS_SYSTEM_PROMPT, get_analysis_prompt

class LLMAnalyzer:
    """大模型分析器"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_base = "https://openrouter.ai/api/v1"
        self.model = os.getenv('OPENROUTER_MODEL', 'minimax/minimax-m2')  # 默认使用Claude
        
        if not self.api_key:
            raise ValueError("缺少OPENROUTER_API_KEY环境变量")
    
    async def analyze_questionnaire(
        self, 
        stats: Dict,
        session_id: str,
        use_simple_prompt: bool = False
    ) -> Dict:
        """
        分析问卷数据
        
        Args:
            stats: 问卷统计数据
            session_id: 会话ID
            use_simple_prompt: 是否使用简化提示词
        
        Returns:
            分析结果字典
        """
        try:
            # 生成提示词
            if use_simple_prompt:
                from prompts import get_simple_analysis_prompt
                user_prompt = get_simple_analysis_prompt(stats)
            else:
                user_prompt = get_analysis_prompt(stats)
            
            # 调用OpenRouter API（返回JSON文本）
            analysis_text = await self._call_openrouter(
                system_prompt=ANALYSIS_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )
            
            # 解析JSON
            import json
            try:
                analysis_json = json.loads(analysis_text)
            except json.JSONDecodeError:
                # 如果解析失败，返回原始文本
                analysis_json = {"raw_text": analysis_text}
            
            return {
                'success': True,
                'session_id': session_id,
                'analysis': analysis_json,  # 现在是JSON对象
                'analysis_text': analysis_text,  # 保留原始文本用于存储
                'model': self.model,
                'total_responses': stats.get('total_responses', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
    
    async def _call_openrouter(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        调用OpenRouter API
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数
            max_tokens: 最大token数
        
        Returns:
            模型返回的文本
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # 可选，用于统计
            "X-Title": "Questionnaire Analysis System"  # 可选
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"}  # 强制JSON输出
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API错误: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # 提取返回的文本
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise Exception(f"OpenRouter返回格式错误: {result}")
    
    def get_available_models(self) -> list:
        """
        获取OpenRouter支持的模型列表
        
        Returns:
            推荐的模型列表
        """
        return [
            {
                "id": "openai/gpt-5.1",
                "name": "gpt-5.1",
                "provider": "openai",
                "description": "高质量分析，推理能力强",
                "recommended": True
            },
            {
                "id": "openai/gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "provider": "OpenAI",
                "description": "强大的通用能力",
                "recommended": True
            },
            {
                "id": "anthropic/claude-3-opus",
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "description": "最强分析能力（较贵）",
                "recommended": False
            },
            {
                "id": "openai/gpt-4o",
                "name": "GPT-4o",
                "provider": "OpenAI",
                "description": "最新的GPT-4优化版本",
                "recommended": True
            },
            {
                "id": "google/gemini-pro-1.5",
                "name": "Gemini Pro 1.5",
                "provider": "Google",
                "description": "长上下文支持",
                "recommended": False
            },
            {
                "id": "qwen/qwen-2.5-72b-instruct",
                "name": "Qwen 2.5 72B",
                "provider": "Alibaba",
                "description": "中文优化，性价比高",
                "recommended": True
            },
            {
                "id": "deepseek/deepseek-chat",
                "name": "DeepSeek Chat",
                "provider": "DeepSeek",
                "description": "性价比极高，中文友好",
                "recommended": True
            }
        ]


# 创建全局实例
try:
    llm_analyzer = LLMAnalyzer()
except ValueError as e:
    print(f"⚠️  LLM分析器初始化失败: {e}")
    print("   如需使用AI分析功能，请在.env中配置OPENROUTER_API_KEY")
    llm_analyzer = None

