from datetime import datetime

from config import settings as root_settings
from db.base import BaseCRUD
from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass
from utils import value
from sqlmodel import SQLModel
from .config import settings
from .exceptions import CoreErrorCode
from .dependencies import CommonsDependencies
from typing import Any, Dict

class BaseServices:
    """
    A base service class that provides common CRUD operations and utilities for interacting with the database.

    This class is designed to work with a CRUD instance derived from `BaseCRUD` and offers methods
    for performing various database operations such as retrieving records by ID or field, saving and updating records,
    and handling soft and hard deletions.

    Args:
        service_name (str): The name of the service.
        crud (BaseCRUD, optional): An instance of a CRUD class derived from `BaseCRUD`. Defaults to None.

    Attributes:
        crud (BaseCRUD): The CRUD instance used for database operations.
        service_name (str): The name of the service.

    """

    def __init__(self, service_name: str, crud: BaseCRUD = None) -> None:
        self.service_name = service_name
        self.ownership_field = settings.ownership_field
        if crud and root_settings.is_production() and isinstance(crud, BaseCRUD) is False:
            raise ValueError(f"The 'crud' attribute must be a BaseCRUD instance for {self.service_name} service.")
        self.crud = crud

    def get_current_datetime(self) -> datetime:
        """
        Returns:
            datetime: ISO 8601 Date Format: YYYY-MM-DD HH:MM:SS.sssZ
        """
        return datetime.now()

    def get_current_user(self, commons: CommonsDependencies):
        """
        Retrieves the current user from the provided common dependencies.

        Args:
            commons (CommonsDependencies): The common dependencies containing the current user information.

        Returns:
            str: The ID of the current user.

        """
        return commons.current_user if commons else None

    def get_current_user_type(self, commons: CommonsDependencies):
        """
        Retrieves the type of the current user from the provided common dependencies.

        Args:
            commons (CommonsDependencies): The common dependencies containing the user type information.

        Returns:
            str: The type of the current user (e.g., admin, customer).

        """
        return commons.user_type if commons else None

    def _build_ownership_query(self, commons: CommonsDependencies = None) -> dict | None:
        """
        Builds a query to filter records based on the ownership of the current user.

        Args:
            commons (CommonsDependencies, optional): The common dependencies containing the current user and user type.

        Returns:
            dict | None: A dictionary representing the ownership query, or None if no ownership query is needed.

        """
        if not commons:
            return None
        current_user_id = self.get_current_user(commons=commons)
        if not current_user_id:
            return None

        current_user_type = self.get_current_user_type(commons=commons)
        if current_user_type == value.UserRoles.ADMIN.value:
            return None

        query = {}
        query[self.ownership_field] = current_user_id
        return query
    
    def _build_query(self, commons: CommonsDependencies = None, query: Dict[str, Any] = None, include_deleted: bool = False) -> dict:
        if not query:
            query = {}
        if not include_deleted:
            query.update({"deleted_at": None})

        # Enhance owner user query
        ownership_query = self._build_ownership_query(commons=commons)
        if ownership_query:
            query.update(ownership_query)
        return query

    async def get_by_id(self, _id: int, commons: CommonsDependencies, ignore_error: bool = False, include_deleted: bool = False) -> SQLModel:
        """
        Retrieves a record by its ID.

        Args:
            _id (int): The ID of the record to retrieve.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found. Defaults to False.
            include_deleted (bool, optional): Whether to include soft-deleted records. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            dict: A dictionary representing the retrieved record.

        Raises:
            CoreErrorCode.NotFound: If the record is not found and `ignore_error` is False.

        """
        query = self._build_query(commons=commons, include_deleted=include_deleted)
        item = await self.crud.get_by_id(session=commons.session, _id=_id, query=query)
        if not item and not ignore_error:
            raise CoreErrorCode.NotFound(service_name=self.service_name, item=_id)
        return item

    async def get_all(
        self,
        commons: CommonsDependencies,
        query: dict = None,
        search: str = None,
        search_in: list = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        order_by: str = "desc",
        include_deleted: bool = False
    ) -> dict:
        """
        Retrieves all records based on the provided query parameters.

        Args:
            query (dict, optional): A dictionary containing filter conditions. Defaults to None.
            search (str, optional): A search string to apply across specified fields. Defaults to None.
            search_in (list, optional): A list of fields to search within. Defaults to None.
            page (int, optional): The page number for pagination. Defaults to 1.
            limit (int, optional): The number of records to retrieve per page. Defaults to 20.
            sort_by (str, optional): The field to sort the results by. Defaults to "created_at".
            order_by (str, optional): The sort order, either "asc" or "desc". Defaults to "desc".
            include_deleted (bool, optional): Whether to include soft-deleted records. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved records and additional metadata.

        """
        query = self._build_query(commons=commons, query=query, include_deleted=include_deleted)

        item = await self.crud.get_all(session=commons.session, query=query, search=search, search_in=search_in, page=page, limit=limit, sort_by=sort_by, order_by=order_by)
        return item

    async def get_by_field(
        self, data: str, field_name: str, commons: CommonsDependencies, ignore_error: bool = False, include_deleted: bool = False) -> list[SQLModel]:
        """
        Retrieves a record by a specific field value.

        Args:
            data (str): The value to search for within the specified field.
            field_name (str): The name of the field to search within.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found. Defaults to False.
            include_deleted (bool, optional): Whether to include soft-deleted records. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            list: A list representing the retrieved record.

        Raises:
            CoreErrorCode.NotFound: If the record is not found and `ignore_error` is False.

        """
        query = self._build_query(commons=commons, include_deleted=include_deleted)

        items = await self.crud.get_by_field(session=commons.session, data=data, field_name=field_name, query=query)
        if not items and not ignore_error:
            raise CoreErrorCode.NotFound(service_name=self.service_name, item=data)
        return items

    async def _check_unique(self, data: SQLModel, unique_field: str | list, ignore_error: bool = False) -> bool:
        """
        Checks if a field or set of fields is unique within the database.

        Args:
            data (SQLModel): The data to check for uniqueness.
            unique_field (str | list): The field or fields to check for uniqueness.
            ignore_error (bool, optional): Whether to ignore errors if a conflict is found. Defaults to False.

        Returns:
            bool: True if the field or fields are unique, False otherwise.

        Raises:
            CoreErrorCode.Conflict: If a conflict is detected and `ignore_error` is False.

        """
        unique_field = [unique_field] if type(unique_field) is str else unique_field
        query = {}
        for field in unique_field:
            if getattr(data, field):
                query[field] = getattr(data, field)
        if not query:
            return False
        total_items = await self.crud.count_documents(query=query)
        if total_items == 0:
            return True
        if ignore_error:
            return False
        first_item = next(iter(query.values()))
        raise CoreErrorCode.Conflict(service_name=self.service_name, item=first_item)

    async def save(self, data: SQLModel, commons: CommonsDependencies) -> SQLModel:
        """
        Saves a new record to the database.

        Args:
            data (SQLModel): The data to be saved.

        Returns:
            dict: The saved record, retrieved by its ID.
        """
        result = await self.crud.save(session=commons.session, data=data)
        return result

    async def save_many(self, data: list[SQLModel], commons: CommonsDependencies) -> list[SQLModel]:
        """
        Saves multiple records to the database.

        Args:
            data (list[SQLModel]): A list of dictionaries, each representing a record to be saved.

        Returns:
            list[dict]: A list of saved records, each retrieved by its ID.

        """
        results = await self.crud.save_many(session=commons.session, data=data)
        return results
    
    async def save_unique(self, data: SQLModel, unique_field: str | list, commons: CommonsDependencies, ignore_error: bool = False) -> bool | SQLModel:
        """
        Saves a new record to the database, ensuring that specified fields are unique. 

        Args:
            data (SQLModel): The data to be saved.
            unique_field (str | list): The field or fields that must be unique in the database.
            ignore_error (bool, optional): Whether to ignore errors if a conflict is found. Defaults to False.

        Returns:
            bool | SQLModel: The saved record, retrieved by its ID.

        Raises:
            CoreErrorCode.Conflict: If a conflict is detected and `ignore_error` is False.
        """
        result = await self.crud.save_unique(session=commons.session, data=data, unique_field=unique_field)
        if not result:
            if ignore_error:
                return False
            else:
                if isinstance(unique_field, list):
                    unique_value = getattr(data, unique_field[0])
                else:
                    unique_value = getattr(data, unique_field)
                raise CoreErrorCode.Conflict(service_name=self.service_name, item=unique_value)
        return result

    async def update_by_id(
        self, _id: int, data: SQLModel, commons: CommonsDependencies, unique_field: str | list = None, check_modified: bool = True, ignore_error: bool = False, include_deleted: bool = False) -> SQLModel | None:
        """
        Updates a record by its ID.

        Args:
            _id (int): The ID of the record to update.
            data (SQLModel): The new data to update the record with.
            unique_field (str | list, optional): The field or fields that must be unique in the database. Defaults to None.
            check_modified (bool, optional): Whether to check if the data has been modified before updating. Defaults to True.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found or not modified. Defaults to False.
            include_deleted (bool, optional): Whether to include soft-deleted records in the update. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            SQLModel | None: The updated record, or None if `ignore_error` is True and the record is not found.

        Raises:
            CoreErrorCode.NotFound: If the record is not found and `ignore_error` is False.
            CoreErrorCode.NotModified: If the record is not modified and `ignore_error` is False.
            CoreErrorCode.Conflict: If a conflict is detected in the unique fields and `ignore_error` is False.

        """
        query = self._build_query(commons=commons, include_deleted=include_deleted)
        item = await self.get_by_id(_id=_id, commons=commons, ignore_error=ignore_error, include_deleted=include_deleted)
        if check_modified:
            is_modified = any(getattr(item, key) != value and key not in settings.fields_not_modified for key, value in data.model_dump(exclude_unset=True).items())
            if not is_modified:
                if not ignore_error:
                    raise CoreErrorCode.NotModified(service_name=self.service_name)
                return None
        if unique_field:
            await self._check_unique(data=data, unique_field=unique_field, ignore_error=ignore_error)
        return await self.crud.update_by_id(session=commons.session, _id=_id, data=data, query=query)

    async def hard_delete_by_id(self, _id: int, commons: CommonsDependencies, ignore_error: bool = False, include_deleted: bool = False) -> bool:
        """
        Permanently deletes a record by its ID.

        Args:
            _id (int): The ID of the record to delete.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found. Defaults to False.
            include_deleted (bool, optional): Whether to include soft-deleted records in the deletion. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            bool: True if the record was successfully deleted, False otherwise.

        Raises:
            CoreErrorCode.NotFound: If the record is not found and `ignore_error` is False.

        """
        query = self._build_query(commons=commons, include_deleted=include_deleted)
        result = await self.crud.delete_by_id(session=commons.session, _id=_id, query=query)
        if not result:
            if not ignore_error:
                raise CoreErrorCode.NotFound(service_name=self.service_name, item=_id)
            return False
        return result

    async def soft_delete_by_id(self, _id: int, commons: CommonsDependencies, ignore_error: bool = False) -> SQLModel:
        """
        Soft deletes a record by its ID.

        Args:
            _id (int): The ID of the record to soft delete.
            ignore_error (bool, optional): Whether to ignore errors if the record is not found. Defaults to False.
            commons (CommonsDependencies, optional): Common dependencies for the request. Defaults to None.

        Returns:
            dict: The updated record with the soft delete information.
        """
        if getattr(self.crud.model, "deleted_at", None) is None or getattr(self.crud.model, "deleted_by", None) is None:
            raise AttributeError("The model must have a 'deleted_at' field to support soft deletions")
        data = self.crud.model()
        data.deleted_at = self.get_current_datetime()
        data.deleted_by = self.get_current_user(commons=commons)
        result = await self.update_by_id(_id=_id, data=data, commons=commons, ignore_error=ignore_error)
        return result
