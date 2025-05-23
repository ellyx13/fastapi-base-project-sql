from core.controllers import BaseControllers
from core.dependencies import CommonsDependencies

from . import schemas
from .services import task_services, TaskServices
from .models import Tasks

class TaskControllers(BaseControllers[TaskServices]):
    def __init__(self) -> None:
        super().__init__(controller_name="tasks", service=task_services)

    async def create(self, data: schemas.CreateRequest, commons: CommonsDependencies) -> Tasks:
        return await self.service.create(data=data, commons=commons)

    async def edit(self, _id: int, data: schemas.EditRequest, commons: CommonsDependencies) -> Tasks:
        await self.get_by_id(_id=_id, commons=commons)
        return await self.service.edit(_id=_id, data=data, commons=commons)


task_controllers = TaskControllers()
