from core.controllers import BaseControllers
from core.services import BaseServices
from users.controllers import user_controllers
from core.dependencies import CommonsDependencies
from . import schemas
from .services import auth_services

class AuthControllers(BaseControllers):
    def __init__(self, controller_name: str, service: BaseServices = None) -> None:
        super().__init__(controller_name, service)

    async def register_user(self, data: schemas.RegisterRequest, commons: CommonsDependencies) -> schemas.LoginResponse:
        user = await user_controllers.register(fullname=data.fullname, email=data.email, password=data.password, phone_number=data.phone_number, commons=commons)
        extra_data = {}
        extra_data["access_token"] = await self.service.create_access_token(user_id=user.id, user_type=user.type)
        return self.convert_orm_to_schema(schema=schemas.LoginResponse, data=user, extra_data=extra_data)


    async def login_user(self, data: schemas.LoginRequest, commons: CommonsDependencies) -> schemas.LoginResponse:
        user = await user_controllers.login(email=data.email, password=data.password, commons=commons)
        extra_data = {}
        extra_data["access_token"] = await self.service.create_access_token(user_id=user.id, user_type=user.type)
        return self.convert_orm_to_schema(schema=schemas.LoginResponse, data=user, extra_data=extra_data)


auth_controllers = AuthControllers(controller_name="auth", service=auth_services)
