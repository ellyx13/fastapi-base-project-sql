from auth.services import auth_services
from core.dependencies import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from utils import value
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas
from .config import settings
from .exceptions import UserErrorCode
from .models import Users
from sqlmodel import Field, SQLModel

class UserServices(BaseServices):
    def __init__(self, service_name, crud=None):
        super().__init__(service_name, crud)

    async def get_by_email(self, email: str, commons: CommonsDependencies, ignore_error: bool = False) -> Users:
        results = await self.get_by_field(data=email, field_name="email", commons=commons, ignore_error=ignore_error)
        return results[0] if results else None

    async def register(self, fullname: str, email: str, password: str, commons: CommonsDependencies, phone_number: str = None) -> Users:
        data = Users(fullname=fullname, email=email, password=password)
        if phone_number:
            data.phone_number = phone_number
        if commons.current_user:
            data.created_by = commons.current_user
        # Set the user role to 'USER' by default.
        data.type = value.UserRoles.USER.value
        # Add the current datetime as the creation time. 
        data.created_at = self.get_current_datetime()
        # Hash the provided password using bcrypt with a generated salt.
        data.password = await auth_services.hash(value=data.password)
        # Save the user, ensuring the email is unique, using the save_unique function.
        user = await self.save_unique(data=data, unique_field="email", commons=commons)
        return user

    async def login(self, email: str, password: str, commons: CommonsDependencies) -> Users:
        user = await self.get_by_email(email=email, commons=commons, ignore_error=True)
        if not user:
            raise UserErrorCode.Unauthorize()
        # Validate the provided password against the hashed value.
        is_valid_password = await auth_services.validate_hash(value=password, hashed_value=user.password)
        if not is_valid_password:
            raise UserErrorCode.Unauthorize()
        return user

    async def edit(self, _id: int, data: Users, commons: CommonsDependencies) -> Users:
        data.updated_at = self.get_current_datetime()
        data.updated_by = self.get_current_user(commons=commons)
        return await self.update_by_id(_id=_id, data=data, commons=commons)

    async def grant_admin(self, _id: int, commons: CommonsDependencies) -> Users:
        user = await self.get_by_id(_id=_id, commons=commons)
        user.type = value.UserRoles.ADMIN.value
        return await self.edit(_id=_id, data=user, commons=commons)  

    async def create_admin(self, session:AsyncSession):
        commons = CommonsDependencies.from_session(session=session)
        admin = await self.get_by_field(data=settings.default_admin_email, field_name="email", commons=commons, ignore_error=True)
        if admin:
            return admin
        admin = await self.register(fullname="Admin", email=settings.default_admin_email, password=settings.default_admin_password, commons=commons)
        print("Admin: ", admin) 
        return await self.grant_admin(_id=admin.id, commons=commons)


user_crud = BaseCRUD(model=models.Users)
user_services = UserServices(service_name="users", crud=user_crud)
