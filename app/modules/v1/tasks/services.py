from core.dependencies import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from db.engine import db_engine

from . import schemas, internal_models
from .models import Tasks

class TaskServices(BaseServices[Tasks]):
    def __init__(self, crud=None):
        super().__init__(service_name="tasks", crud=crud, model=Tasks)

    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> Tasks:
        data = Tasks.from_create_request(data=data, created_by=commons.current_user)
        return await self.save(data=data, commons=commons)

    async def edit(self, _id: int, data: schemas.EditRequest, commons: CommonsDependencies) -> Tasks:
        data = internal_models.EditWithAudit(summary=data.summary, description=data.description, status=data.status, updated_by=commons.current_user)
        return await self.update_by_id(_id=_id, data=data, commons=commons)


task_crud = BaseCRUD(model=Tasks)
task_services = TaskServices(crud=task_crud)
