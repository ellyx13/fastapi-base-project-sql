from core.controllers import BaseControllers
from core.dependencies import CommonsDependencies
from . import schemas
from .services import user_services, UserServices
from .models import Users

class UserControllers(BaseControllers[UserServices]):
    def __init__(self) -> None:
        super().__init__(controller_name="users", service=user_services)

    async def register(self, fullname: str, email: str, password: str, commons: CommonsDependencies, phone_number: str = None) -> Users:
        return await self.service.register(fullname=fullname, email=email, password=password, phone_number=phone_number, commons=commons)

    async def login(self, email: str, password: str, commons: CommonsDependencies) -> Users:
        return await self.service.login(email=email, password=password, commons=commons)

    async def get_me(self, commons: CommonsDependencies) -> Users:
        current_user_id = self.get_current_user(commons=commons)
        return await self.get_by_id(_id=current_user_id, commons=commons)

    async def edit(self, _id: int, data: schemas.EditRequest, commons: CommonsDependencies) -> Users:
        # Check if that user id exists or not
        await self.get_by_id(_id=_id, commons=commons)
        return await self.service.edit(_id=_id, data=data, commons=commons)
    
    async def edit_me(self, data: schemas.EditRequest, commons: CommonsDependencies) -> Users:
        _id = self.get_current_user(commons=commons)
        return await self.edit(_id=_id, data=data, commons=commons)


user_controllers = UserControllers()
