from pydantic import BaseModel


class TaskId(BaseModel):
    task_id: str