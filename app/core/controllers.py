from core.dependencies import CommonsDependencies
from .services import BaseServices
from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from sqlmodel import SQLModel

NOT_DECLARED_SERVICE = "Service must be an instance of BaseServices. Maybe the service has not been declared when creating the class Controllers"

TService = TypeVar("TService")

class BaseControllers(Generic[TService]):
    """
    A base class for controllers that provides common methods for interacting with services.

    This class is designed to work with a service instance derived from `BaseServices`. It offers methods
    to perform common operations like retrieving all records, fetching records by ID or field, and soft-deleting records by ID.

    Args:
        controller_name (str): The name of the controller.
        service (BaseServices, optional): An instance of a service class derived from `BaseServices`. Defaults to None.

    Attributes:
        controller_name (str): The name of the controller.
        service (BaseServices): The service instance used for performing operations.
    """

    def __init__(self, controller_name: str, service: TService = None) -> None:
        self.controller_name = controller_name
        self.service = service

    async def get_all(
        self,
        query: dict = None,
        search: str = None,
        search_in: list = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        order_by: str = "desc",
        include_deleted: bool = False,
        commons: CommonsDependencies = None,
    ) -> dict:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        results = await self.service.get_all(
            query=query,
            search=search,
            search_in=search_in,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order_by=order_by,
            include_deleted=include_deleted,
            commons=commons,
        )
        return results

    async def get_by_id(self, _id: int, ignore_error: bool = False, include_deleted: bool = False, commons: CommonsDependencies = None) -> dict:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        result = await self.service.get_by_id(_id=_id, ignore_error=ignore_error, include_deleted=include_deleted, commons=commons)
        return result

    async def get_by_field(
        self, data: str, field_name: str, ignore_error: bool = False, include_deleted: bool = False, commons: CommonsDependencies = None
    ) -> list:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        result = await self.service.get_by_field(data=data, field_name=field_name, ignore_error=ignore_error, include_deleted=include_deleted, commons=commons)
        return result

    async def soft_delete_by_id(self, _id: int, ignore_error: bool = False, commons: CommonsDependencies = None) -> dict:
        if not isinstance(self.service, BaseServices):
            raise TypeError(NOT_DECLARED_SERVICE)
        result = await self.service.soft_delete_by_id(_id=_id, ignore_error=ignore_error, commons=commons)
        return result

    def get_current_user(self, commons: CommonsDependencies):
        return commons.current_user

    def get_current_user_type(self, commons: CommonsDependencies):
        return commons.user_type

    def convert_orm_to_schema(self, schema: Type[BaseModel], data: SQLModel, extra_data: dict = None) -> BaseModel:
        """
        Converts an ORM model (`SQLModel`) into a Pydantic schema (`BaseModel`), ensuring missing fields 
        are handled properly and allowing additional fields to be added dynamically.

        Args:
            schema (Type[BaseModel]): The target Pydantic schema to validate the data.
            data (SQLModel): The ORM model instance retrieved from the database.
            extra_data (dict, optional): Additional key-value pairs to update the schema with.

        Returns:
            BaseModel: An instance of the schema containing the original data and extra fields.
        """
        # Convert ORM model to dictionary, excluding unset (None) fields
        data_dict = data.model_dump()
        # Merge extra data if provided
        if extra_data:
            data_dict.update(extra_data)
        # Validate the dictionary and return a Pydantic schema instance
        return schema.model_validate(data_dict)