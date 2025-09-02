import json
import time
from datetime import datetime, timedelta

from config import settings
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from memu import MemuClient
from pymongo import errors


class ChatMessageHistory(MongoDBChatMessageHistory):
    """Custom chat message history for MongoDB."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collection.create_index("timestamp")

    def add_message(self, message: BaseMessage):
        """Add a message to the history."""
        self.collection.insert_one(
            {
                self.session_id_key: self.session_id,
                self.history_key: json.dumps(message_to_dict(message)),
                "timestamp": message.additional_kwargs.get("chat_timestamp", datetime.now().timestamp()),
            }
        )

    def get_messages_with_time(self, time: timedelta = timedelta(days=2)):
        """Retrieve messages from the last 'time' duration."""
        cutoff_time = datetime.now() - time
        cursor = self.collection.find(
            {
                self.session_id_key: self.session_id,
                "timestamp": {"$gte": cutoff_time.timestamp()},
            }
        ).sort("timestamp", 1)
        if cursor:
            items = [json.loads(document[self.history_key]) for document in cursor]
        else:
            items = []
        messages = messages_from_dict(items)
        return messages

    def get_messages_with_count(self, count: int | None = 5) -> list[BaseMessage]:  # type: ignore
        """Retrieve the messages from MongoDB"""
        cursor = None
        try:
            if not count:
                cursor = self.collection.find({self.session_id_key: self.session_id})
            else:
                skip_count = max(
                    0,
                    self.collection.count_documents({self.session_id_key: self.session_id}) - count,
                )
                cursor = self.collection.find({self.session_id_key: self.session_id}, skip=skip_count)
        except errors.OperationFailure:
            pass

        if cursor:
            items = [json.loads(document[self.history_key]) for document in cursor]
        else:
            items = []

        messages = messages_from_dict(items)
        return messages


def get_memories_client(session_id: str):
    chat_message_history = ChatMessageHistory(
        connection_string=settings.mongo_uri.unicode_string(),
        database_name=settings.MONGO_DB,
        collection_name="chat_histories",
        session_id=session_id,
        history_size=30,
    )
    return chat_message_history


client = MemuClient(
    base_url="https://api.memu.so", 
    api_key=settings.MEMU_API_KEY,
)

def load_memories(uid):
    """加载历史消息"""
    chat_message_history = get_memories_client(uid)  # type: ignore
    history_messages = chat_message_history.get_messages_with_count(100)
    return history_messages

# messages = load_memories("ITFOPZQLOLVI")
# ROLE_MAP = {
#     "human": "user",
#     "ai": "assistant",
# }

# conversation = [
#     {"role": ROLE_MAP[msg.type], "content": msg.text()} for msg in messages
# ]

# # Save to MemU
# memo_response = client.memorize_conversation(
#     conversation=conversation,
#     user_id="demo-1", 
#     user_name="Demo User 1", 
#     agent_id="demo-agent-1", 
#     agent_name="Dempo Assistant 1"
# )
# print(f"💾 Saved! Task ID: {memo_response.task_id}")

# # Wait for completion
# while True:
#     status = client.get_task_status(memo_response.task_id)
#     print(f"Task status: {status.status}")
#     if status.status in ['SUCCESS', 'FAILURE', 'REVOKED']:
#         break
#     time.sleep(2)

# resp = client.retrieve_default_categories(user_id="demo-1", agent_id="demo-agent-1")
# resp = client.retrieve_related_clustered_categories(user_id="test_2", agent_id="fortuneteller001", category_query="事业工作换工作相关咨询")
# resp = client.retrieve_related_clustered_categories(user_id="test_2", agent_id="fortuneteller001", category_query="用户基本信息")
# if resp.clustered_categories:
#     for clustered in resp.clustered_categories:
#         print(clustered.summary)
#         print(clustered.memories)
#         print(clustered.similarity_score)
# print(resp)

resp = client.retrieve_related_memory_items(user_id="test_2", agent_id="fortuneteller001", query="事业工作换工作相关咨询")
if resp.related_memories:
    for memory in resp.related_memories:
        # print("===")
        # print(memory.memory.category)
        print(memory.memory.content)
        # print(f"happened_at: {memory.memory.happened_at}")
        # print(f"created_at: {memory.memory.created_at}")
        # print(f"updated_at: {memory.memory.updated_at}")
        # print(memory.similarity_score)
# print(resp)