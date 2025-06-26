from prisma import Prisma
from prisma.models import Task, Event, Note, LLMConfig
from datetime import datetime

class DatabaseTool:
    def __init__(self):
        self.db = Prisma()

    async def connect_db(self):
        await self.db.connect()

    async def disconnect_db(self):
        await self.db.disconnect()

    # Task CRUD operations
    async def create_task(self, title: str, description: str = None, due_date: datetime = None, priority: str = "medium", status: str = "pending", user_id: str = "default") -> Task:
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
        return task

    async def get_task(self, task_id: str) -> Task | None:
        task = await self.db.task.find_unique(where={"id": task_id})
        return task

    async def get_all_tasks(self, user_id: str = "default") -> list[Task]:
        tasks = await self.db.task.find_many(where={"user_id": user_id})
        return tasks

    async def update_task(self, task_id: str, title: str = None, description: str = None, due_date: datetime = None, priority: str = None, status: str = None) -> Task:
        data = {}
        if title: data["title"] = title
        if description: data["description"] = description
        if due_date: data["due_date"] = due_date
        if priority: data["priority"] = priority
        if status: data["status"] = status

        task = await self.db.task.update(
            where={"id": task_id},
            data=data,
        )
        return task

    async def delete_task(self, task_id: str) -> Task:
        task = await self.db.task.delete(where={"id": task_id})
        return task

    # Event CRUD operations
    async def create_event(self, title: str, description: str = None, start_time: datetime = None, end_time: datetime = None, location: str = None, user_id: str = "default") -> Event:
        event = await self.db.event.create(
            data={
                "title": title,
                "description": description,
                "start_time": start_time,
                "end_time": end_time,
                "location": location,
                "user_id": user_id,
            }
        )
        return event

    async def get_event(self, event_id: str) -> Event | None:
        event = await self.db.event.find_unique(where={"id": event_id})
        return event

    async def get_all_events(self, user_id: str = "default") -> list[Event]:
        events = await self.db.event.find_many(where={"user_id": user_id})
        return events

    async def update_event(self, event_id: str, title: str = None, description: str = None, start_time: datetime = None, end_time: datetime = None, location: str = None) -> Event:
        data = {}
        if title: data["title"] = title
        if description: data["description"] = description
        if start_time: data["start_time"] = start_time
        if end_time: data["end_time"] = end_time
        if location: data["location"] = location

        event = await self.db.event.update(
            where={"id": event_id},
            data=data,
        )
        return event

    async def delete_event(self, event_id: str) -> Event:
        event = await self.db.event.delete(where={"id": event_id})
        return event

    # Note CRUD operations
    async def create_note(self, title: str, content: str, user_id: str = "default") -> Note:
        note = await self.db.note.create(
            data={
                "title": title,
                "content": content,
                "user_id": user_id,
            }
        )
        return note

    async def get_note(self, note_id: str) -> Note | None:
        note = await self.db.note.find_unique(where={"id": note_id})
        return note

    async def get_all_notes(self, user_id: str = "default") -> list[Note]:
        notes = await self.db.note.find_many(where={"user_id": user_id})
        return notes

    async def update_note(self, note_id: str, title: str = None, content: str = None) -> Note:
        data = {}
        if title: data["title"] = title
        if content: data["content"] = content

        note = await self.db.note.update(
            where={"id": note_id},
            data=data,
        )
        return note

    async def delete_note(self, note_id: str) -> Note:
        note = await self.db.note.delete(where={"id": note_id})
        return note

    # LLMConfig CRUD operations
    async def create_llm_config(self, model_name: str, api_key: str, temperature: float = 0.7, max_tokens: int = None, user_id: str = "default") -> LLMConfig:
        llm_config = await self.db.llmconfig.create(
            data={
                "model_name": model_name,
                "api_key": api_key,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "user_id": user_id,
            }
        )
        return llm_config

    async def get_llm_config(self, llm_config_id: str) -> LLMConfig | None:
        llm_config = await self.db.llmconfig.find_unique(where={"id": llm_config_id})
        return llm_config

    async def get_all_llm_configs(self, user_id: str = "default") -> list[LLMConfig]:
        llm_configs = await self.db.llmconfig.find_many(where={"user_id": user_id})
        return llm_configs

    async def update_llm_config(self, llm_config_id: str, model_name: str = None, api_key: str = None, temperature: float = None, max_tokens: int = None) -> LLMConfig:
        data = {}
        if model_name: data["model_name"] = model_name
        if api_key: data["api_key"] = api_key
        if temperature: data["temperature"] = temperature
        if max_tokens: data["max_tokens"] = max_tokens

        llm_config = await self.db.llmconfig.update(
            where={"id": llm_config_id},
            data=data,
        )
        return llm_config

    async def delete_llm_config(self, llm_config_id: str) -> LLMConfig:
        llm_config = await self.db.llmconfig.delete(where={"id": llm_config_id})
        return llm_config 