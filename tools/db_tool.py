from prisma import Prisma
from prisma.models import Task, Event, Note, LLMConfig
from datetime import datetime

db = Prisma()

async def connect_db():
    await db.connect()

async def disconnect_db():
    await db.disconnect()

# Task CRUD operations
async def create_task(title: str, description: str = None, due_date: datetime = None, priority: str = "medium", status: str = "pending", user_id: str = "default") -> Task:
    task = await db.task.create(
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

async def get_task(task_id: str) -> Task | None:
    task = await db.task.find_unique(where={"id": task_id})
    return task

async def get_all_tasks(user_id: str = "default") -> list[Task]:
    tasks = await db.task.find_many(where={"user_id": user_id})
    return tasks

async def update_task(task_id: str, title: str = None, description: str = None, due_date: datetime = None, priority: str = None, status: str = None) -> Task:
    data = {}
    if title: data["title"] = title
    if description: data["description"] = description
    if due_date: data["due_date"] = due_date
    if priority: data["priority"] = priority
    if status: data["status"] = status

    task = await db.task.update(
        where={"id": task_id},
        data=data,
    )
    return task

async def delete_task(task_id: str) -> Task:
    task = await db.task.delete(where={"id": task_id})
    return task

# Event CRUD operations
async def create_event(title: str, description: str = None, start_time: datetime = None, end_time: datetime = None, location: str = None, user_id: str = "default") -> Event:
    event = await db.event.create(
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

async def get_event(event_id: str) -> Event | None:
    event = await db.event.find_unique(where={"id": event_id})
    return event

async def get_all_events(user_id: str = "default") -> list[Event]:
    events = await db.event.find_many(where={"user_id": user_id})
    return events

async def update_event(event_id: str, title: str = None, description: str = None, start_time: datetime = None, end_time: datetime = None, location: str = None) -> Event:
    data = {}
    if title: data["title"] = title
    if description: data["description"] = description
    if start_time: data["start_time"] = start_time
    if end_time: data["end_time"] = end_time
    if location: data["location"] = location

    event = await db.event.update(
        where={"id": event_id},
        data=data,
    )
    return event

async def delete_event(event_id: str) -> Event:
    event = await db.event.delete(where={"id": event_id})
    return event

# Note CRUD operations
async def create_note(title: str, content: str, user_id: str = "default") -> Note:
    note = await db.note.create(
        data={
            "title": title,
            "content": content,
            "user_id": user_id,
        }
    )
    return note

async def get_note(note_id: str) -> Note | None:
    note = await db.note.find_unique(where={"id": note_id})
    return note

async def get_all_notes(user_id: str = "default") -> list[Note]:
    notes = await db.note.find_many(where={"user_id": user_id})
    return notes

async def update_note(note_id: str, title: str = None, content: str = None) -> Note:
    data = {}
    if title: data["title"] = title
    if content: data["content"] = content

    note = await db.note.update(
        where={"id": note_id},
        data=data,
    )
    return note

async def delete_note(note_id: str) -> Note:
    note = await db.note.delete(where={"id": note_id})
    return note

# LLMConfig CRUD operations
async def create_llm_config(model_name: str, api_key: str, temperature: float = 0.7, max_tokens: int = None, user_id: str = "default") -> LLMConfig:
    llm_config = await db.llmconfig.create(
        data={
            "model_name": model_name,
            "api_key": api_key,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "user_id": user_id,
        }
    )
    return llm_config

async def get_llm_config(llm_config_id: str) -> LLMConfig | None:
    llm_config = await db.llmconfig.find_unique(where={"id": llm_config_id})
    return llm_config

async def get_all_llm_configs(user_id: str = "default") -> list[LLMConfig]:
    llm_configs = await db.llmconfig.find_many(where={"user_id": user_id})
    return llm_configs

async def update_llm_config(llm_config_id: str, model_name: str = None, api_key: str = None, temperature: float = None, max_tokens: int = None) -> LLMConfig:
    data = {}
    if model_name: data["model_name"] = model_name
    if api_key: data["api_key"] = api_key
    if temperature: data["temperature"] = temperature
    if max_tokens: data["max_tokens"] = max_tokens

    llm_config = await db.llmconfig.update(
        where={"id": llm_config_id},
        data=data,
    )
    return llm_config

async def delete_llm_config(llm_config_id: str) -> LLMConfig:
    llm_config = await db.llmconfig.delete(where={"id": llm_config_id})
    return llm_config