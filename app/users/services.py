from auth.services import auth_services
from core.dependencies import CommonsDependencies
from core.services import BaseServices
from db.base import BaseCRUD
from utils import value
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas, internal_models
from .config import settings
from .exceptions import UserErrorCode
from .models import Users
from sqlmodel import Field, SQLModel

class UserServices(BaseServices[Users]):
    def __init__(self, crud = None):
        super().__init__(service_name="users", crud=crud, model=Users)

    async def get_by_email(self, email: str, commons: CommonsDependencies, ignore_error: bool = False) -> Users:
        results = await self.get_by_field(data=email, field_name="email", commons=commons, ignore_error=ignore_error)
        return results[0] if results else None

    async def register(self, fullname: str, email: str, password: str, commons: CommonsDependencies, phone_number: str = None) -> Users:
        data = Users(fullname=fullname, email=email, password=password)
        if phone_number:
            data.phone_number = phone_number
        if self.get_current_user(commons=commons):
            data.created_by = self.get_current_user(commons=commons)
        # Set the user role to 'USER' by default.
        data.type = value.UserRoles.USER.value
        # Add the current datetime as the creation time. 
        data.created_at = self.get_current_datetime()
        # Hash the provided password using bcrypt with a generated salt.
        data.password = await auth_services.hash(value=data.password)
        # Save the user, ensuring the email is unique, using the save_unique function.
        user = await self.save_unique(data=data, unique_field="email", commons=commons)
        
        data_update = internal_models.UpdateCreatedBy(created_by=user.id)
        user = await self.update_by_id(_id=user.id, data=data_update, commons=commons)
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

    async def edit(self, _id: int, data: schemas.EditRequest | Users, commons: CommonsDependencies) -> Users:
        data = internal_models.EditWithAudit(fullname=data.fullname, phone=data.phone_number, updated_by=commons.current_user)
        return await self.update_by_id(_id=_id, data=data, commons=commons)

    async def grant_admin(self, _id: int, commons: CommonsDependencies) -> Users:
        data = internal_models.GrantAdmin(updated_by=commons.current_user)
        return await self.update_by_id(_id=_id, data=data, commons=commons)  

    async def create_admin(self, session:AsyncSession):
        commons = CommonsDependencies.from_session(session=session)
        admin = await self.get_by_field(data=settings.default_admin_email, field_name="email", commons=commons, ignore_error=True)
        if admin:
            return admin
        admin = await self.register(fullname="Admin", email=settings.default_admin_email, password=settings.default_admin_password, commons=commons)
        return await self.grant_admin(_id=admin.id, commons=commons)


user_crud = BaseCRUD(model=models.Users)
user_services = UserServices(crud=user_crud)
