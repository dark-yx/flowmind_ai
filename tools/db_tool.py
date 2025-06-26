from prisma import Prisma
from prisma.models import Task, Event, Note, LLMConfig
from datetime import datetime
from typing import List, Optional, Dict, Any

class DBTool:
    def __init__(self):
        self.db = Prisma()

    async def connect(self):
        await self.db.connect()

    async def disconnect(self):
        await self.db.disconnect()

    async def create_task(self, title: str, user_id: str, description: Optional[str] = None, due_date: Optional[datetime] = None, priority: str = "medium", status: str = "pending") -> Dict[str, Any]:
        task = await self.db.task.create(
            data={
                "title": title,
                "description": description,
                "due_date": due_date,
                "priority": priority,
                "status": status,
                "user_id": user_id,
            }
        )
        return task.dict()

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = await self.db.task.find_unique(where={"id": task_id})
        return task.dict() if task else None

    async def update_task(self, task_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        task = await self.db.task.update(where={"id": task_id}, data=data)
        return task.dict() if task else None

    async def delete_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = await self.db.task.delete(where={"id": task_id})
        return task.dict() if task else None

    async def list_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        tasks = await self.db.task.find_many(where={"user_id": user_id})
        return [task.dict() for task in tasks]

    async def create_event(self, title: str, start_time: datetime, end_time: datetime, user_id: str, description: Optional[str] = None, location: Optional[str] = None) -> Dict[str, Any]:
        event = await self.db.event.create(
            data={
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                "description": description,
                "location": location,
                "user_id": user_id,
            }
        )
        return event.dict()

    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        event = await self.db.event.find_unique(where={"id": event_id})
        return event.dict() if event else None

    async def update_event(self, event_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        event = await self.db.event.update(where={"id": event_id}, data=data)
        return event.dict() if event else None

    async def delete_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        event = await self.db.event.delete(where={"id": event_id})
        return event.dict() if event else None

    async def list_events(self, user_id: str) -> List[Dict[str, Any]]:
        events = await self.db.event.find_many(where={"user_id": user_id})
        return [event.dict() for event in events]

    async def create_note(self, title: str, content: str, user_id: str) -> Dict[str, Any]:
        note = await self.db.note.create(
            data={
                "title": title,
                "content": content,
                "user_id": user_id,
            }
        )
        return note.dict()

    async def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        note = await self.db.note.find_unique(where={"id": note_id})
        return note.dict() if note else None

    async def update_note(self, note_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        note = await self.db.note.update(where={"id": note_id}, data=data)
        return note.dict() if note else None

    async def delete_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        note = await self.db.note.delete(where={"id": note_id})
        return note.dict() if note else None

    async def list_notes(self, user_id: str) -> List[Dict[str, Any]]:
        notes = await self.db.note.find_many(where={"user_id": user_id})
        return [note.dict() for note in notes]

    async def create_llm_config(self, model_name: str, api_key: str, user_id: str, temperature: float = 0.7, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        llm_config = await self.db.llmconfig.create(
            data={
                "model_name": model_name,
                "api_key": api_key,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "user_id": user_id,
            }
        )
        return llm_config.dict()

    async def get_llm_config(self, llm_config_id: str) -> Optional[Dict[str, Any]]:
        llm_config = await self.db.llmconfig.find_unique(where={"id": llm_config_id})
        return llm_config.dict() if llm_config else None

    async def update_llm_config(self, llm_config_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        llm_config = await self.db.llmconfig.update(where={"id": llm_config_id}, data=data)
        return llm_config.dict() if llm_config else None

    async def delete_llm_config(self, llm_config_id: str) -> Optional[Dict[str, Any]]:
        llm_config = await self.db.llmconfig.delete(where={"id": llm_config_id})
        return llm_config.dict() if llm_config else None

    async def list_llm_configs(self, user_id: str) -> List[Dict[str, Any]]:
        llm_configs = await self.db.llmconfig.find_many(where={"user_id": user_id})
        return [llm_config.dict() for llm_config in llm_configs] 