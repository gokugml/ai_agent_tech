"""记忆存储节点"""

import time
from typing import List, Dict, Any

from langchain_core.messages import AIMessage, HumanMessage

from config import settings
from memu import MemuClient

# MemU客户端配置
memu_client = MemuClient(
    base_url="https://api.memu.so", 
    api_key=settings.MEMU_API_KEY,
)
from test_chatbot_memu.state import ChatbotState


def memory_store_node(state: ChatbotState) -> ChatbotState:
    """记忆存储节点
    
    自动提取最新的用户-助手对话对，存储到MemU记忆系统
    """
    messages = state["messages"]
    session_id = state["session_id"]
    
    # 如果消息数少于2条，无需存储
    if len(messages) < 2:
        return {}
    
    # 提取最新的对话对（用户消息 + AI响应）
    latest_messages = list(messages)[-2:]  # 获取最后两条消息
    
    # 确保是用户消息 + AI消息的配对
    user_message = None
    ai_message = None
    
    for msg in latest_messages:
        if isinstance(msg, HumanMessage) and user_message is None:
            user_message = msg
        elif isinstance(msg, AIMessage) and ai_message is None:
            ai_message = msg
    
    # 只有完整的对话对才进行存储
    if user_message and ai_message:
        try:
            # 使用Message.text()方法提取文本内容
            conversation = [
                {"role": "user", "content": user_message.text()},
                {"role": "assistant", "content": ai_message.text()}
            ]
            
            # 调用MemU API存储对话
            memo_response = memu_client.memorize_conversation(
                conversation=conversation,
                user_id=session_id,  # 使用session_id作为用户ID
                user_name=f"User_{session_id}",
                agent_id="chatbot_memu",
                agent_name="ChatBot MemU"
            )
            
            print(f"💾 记忆已存储! Task ID: {memo_response.task_id}")
            
            # 可选：等待存储完成（简化版本，实际应用中可能需要后台处理）
            max_wait_time = 10  # 最大等待10秒
            wait_time = 0
            while wait_time < max_wait_time:
                try:
                    status = memu_client.get_task_status(memo_response.task_id)
                    if status.status in ['SUCCESS', 'FAILURE', 'REVOKED']:
                        print(f"📝 记忆存储状态: {status.status}")
                        break
                except Exception:
                    # 忽略状态查询失败，不影响主流程
                    break
                time.sleep(1)
                wait_time += 1
                
        except Exception as e:
            print(f"❌ 记忆存储失败: {str(e)}")
    
    # 返回空状态，不修改对话状态
    return {}