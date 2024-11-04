from pydantic import BaseModel, Field
from typing import List, Optional

from enums import TaskPriority, TaskStatus


class KPIModel(BaseModel):
    domain: str
    relevant_kpi: str
    questions: List[str]


class Task(BaseModel):
    task_name: str
    task_details: str
    task_priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM)
    task_status: Optional[TaskStatus] = Field(default=TaskStatus.PENDING)


class TaskList(BaseModel):
    tasks: List[Task] = Field(..., min_items=1)


class EmailOutputModel(BaseModel):
    recipients_email: Optional[List[str]]
    recipient_type: Optional[str]
    body: str
    subject: str
    sign_off: str


class EmailModel(BaseModel):
    emails: List[EmailOutputModel] = Field(..., min_items=1)
