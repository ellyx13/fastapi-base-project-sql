from core.dependencies import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import db_engine

from . import schemas
from .models import Tasks

class TaskServices(BaseServices):
    def __init__(self, service_name, crud=None):
        super().__init__(service_name, crud)

    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> Tasks:
        data = Tasks(**data.model_dump())
        data.status = "to_do"
        data.created_by = self.get_current_user(commons=commons)
        data.created_at = self.get_current_datetime()
        return await self.save(data=data, commons=commons)

    async def edit(self, _id: int, data: schemas.EditRequest, commons: CommonsDependencies) -> Tasks:
        data = Tasks(**data.model_dump(exclude_none=True))
        data.updated_by = self.get_current_user(commons=commons)
        data.updated_at = self.get_current_datetime()
        return await self.update_by_id(_id=_id, data=data, commons=commons)


task_crud = BaseCRUD(model=Tasks)
task_services = TaskServices(service_name="tasks", crud=task_crud)
