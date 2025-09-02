import json
from datetime import datetime, timedelta

from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from pymongo import errors

from user_config import settings


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
