from sqlmodel import SQLModel, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union, Any, Optional, Dict
from sqlalchemy import asc, desc
import re
import math

class BaseCRUD:
    """
    Base CRUD class for SQLAlchemy models.

    Attributes:
        model (Type[SQLModel]): The SQLModel class representing the database table.
    """

    def __init__(self, model: type[SQLModel]) -> None:
        """
        Initialize the CRUD class with the model.

        Args:
            model (Type[SQLModel]): The SQLModel class.
        """
        self.model = model

    async def count(self, session: AsyncSession) -> int:
        """
        Count the total number of records in the table.

        Args:
            session (AsyncSession): The database session.

        Returns:
            int: The total count of records.
        """
        statement = select(self.model)
        result = await session.exec(statement)
        return len(result.all())

    def convert_bools(self, value: Union[dict, list, str, Any]) -> Union[dict, list, str, Any]:
        """
        Converts string representations of booleans ("true" or "false") to actual boolean values (True, False) in a given data structure.

        Args:
            value (dict | list | str | Any): The data structure containing the values to be converted.
                                             It can be a dictionary, list, string, or any other data type.

        Returns:
            dict | list | str | Any: The data structure with boolean string values converted to actual booleans.
        """
        bool_map = {"false": False, "true": True}

        if isinstance(value, dict):
            return {key: self.convert_bools(val) for key, val in value.items()}
        elif isinstance(value, list):
            return [self.convert_bools(item) for item in value]
        elif isinstance(value, str):
            return bool_map.get(value.lower(), value)
        return value

    def replace_special_chars(self, value: Union[dict, str, Any]) -> Union[dict, str, Any]:
        """
        Escapes special characters in strings within a given dictionary or string.

        This function finds special characters that have specific meanings in regular expressions
        (e.g., *, +, ?, ^, $, {, }, (, ), |, [, ], \\) and escapes them by prefixing them with a backslash.
        
        Args:
            value (dict | str | Any): The input dictionary or string containing special characters.

        Returns:
            dict | str | Any: The input dictionary with all string values having special characters escaped,
                              or a single string with special characters escaped using a backslash.
        """
        pattern = r"([*+?^${}()|[\]\\])"

        if isinstance(value, dict):
            return {
                key: self.replace_special_chars(val)
                for key, val in value.items()
            }
        elif isinstance(value, list):
            return [self.replace_special_chars(item) for item in value]
        elif isinstance(value, str):
            return re.sub(pattern, r"\\\1", value)
        
        # Return unchanged for non-string, non-dict, non-list values
        return value
    
    def build_query_filters(self, _id: int, query: Dict[str, Any]) -> List[Any]:
        """
        Constructs a list of query filters based on the record ID and additional query criteria.

        Args:
            _id (int): The ID of the record to be queried.
            query (dict): Additional query criteria to filter the records.

        Returns:
            List[Any]: A list of query filters to be used in select statements.
        """
        filters = [self.model.id == _id]

        if query:
            filters.extend([
                getattr(self.model, key) == value
                for key, value in query.items()
                if hasattr(self.model, key)
            ])

        return filters

    async def save(self, session: AsyncSession, data: SQLModel) -> SQLModel:
        """
        Inserts a single record into the database.

        Args:
            session (AsyncSession): The database session.
            data (dict): The data to be inserted.

        Returns:
            int: The ID of the inserted record.
        """
        session.add(data)
        await session.commit()
        await session.refresh(data)
        return data

    async def save_many(self, session: AsyncSession, data: List[SQLModel]) -> List[SQLModel]:
        """
        Inserts multiple records into the database.

        Args:
            session (AsyncSession): The database session.
            data (List[SQLModel]): List of data dictionaries to insert.

        Returns:
            List[int]: List of inserted record IDs.
        """
        session.add_all(data)
        await session.commit()
        for obj in data:      
            await session.refresh(obj)
        return data
    
    async def save_unique(self, session: AsyncSession, data: SQLModel, unique_field: list | str) -> bool | SQLModel:
        """
        Saves a record into the database if it does not already exist based on unique fields.

        Args:
            session (AsyncSession): The database session.
            data (SQLModel): The data to be inserted.
            unique_field (list | str): The field or list of fields that should be unique.

        Returns:
            bool | SQLModel: The inserted record if successful, or False if it already exists.
        """
        # Build the uniqueness query
        if isinstance(unique_field, list):
            filters = [getattr(self.model, field) == getattr(data, field) for field in unique_field if field in data]
        elif isinstance(unique_field, str):
            filters = [getattr(self.model, unique_field) == getattr(data, unique_field)]
        else:
            raise ValueError("The type of unique_field must be list or str")

        # Execute the uniqueness check
        statement = select(self.model).where(*filters)
        result = await session.exec(statement)
        existing_record = result.first()

        if existing_record:
            return False

        return await self.save(session=session, data=data)
    
    async def update_by_id(
        self, session: AsyncSession, _id: int, data: SQLModel, query: Optional[Dict[str, Any]] = None) -> type[SQLModel] | None:
        """
        Updates a record in the database based on its ID and optional query filters.

        Args:
            session (AsyncSession): The database session.
            _id (int): The ID of the record to be updated.
            data (dict): The data to update in the record.
            query (dict, optional): Additional query criteria for the update operation.

        Returns:
            dict | None: The updated record as a dictionary if the update was successful, or None if the record doesn't exist.
        """
        # Build the initial query with the ID
        filters = self.build_query_filters(_id=_id, query=query)

        # Execute the select query to check if the record exists
        statement = select(self.model).where(*filters)
        result = await session.exec(statement)
        record = result.one_or_none()

        if not record:
            return None  # Record does not exist or does not match query filters

        data = data.model_dump(exclude_unset=True)
        record.sqlmodel_update(data)
        session.add(record)
        await session.commit()
        await session.refresh(record)  # Refresh to get the updated data from the DB
        return record

    async def delete_by_id(
        self, session: AsyncSession, _id: int, query: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Deletes a record from the database based on its ID and optional query filters.

        Args:
            session (AsyncSession): The database session.
            _id (int): The ID of the record to be deleted.
            query (dict, optional): Additional query criteria for the delete operation.

        Returns:
            bool: True if the record was successfully deleted, False otherwise.
        """
        filters = self.build_query_filters(_id=_id, query=query)

        statement = select(self.model).where(*filters)
        result = await session.exec(statement)
        record = result.one_or_none()

        if not record:
            return False

        await session.delete(record)
        await session.commit()
        return True
    
    async def get_by_id(
        self, session: AsyncSession, _id: int, query: Optional[Dict[str, Any]] = None
    ) -> type[SQLModel] | None: 
        """
        Retrieves a record from the database based on its ID, with optional field limitations and additional query.

        Args:
            session (AsyncSession): The database session.
            _id (int): The ID of the record to be retrieved.
            query (dict, optional): Additional query criteria to further refine the search.

        Returns:
            dict | None: The retrieved record as a dictionary, or None if no record is found.
        """
        filters = self.build_query_filters(_id=_id, query=query)

        statement = select(self.model).where(*filters)
        result = await session.exec(statement)
        record = result.one_or_none()
        if record:
            await session.refresh(record)
            return record
        return None
    
    async def get_by_field(
        self,
        session: AsyncSession,
        data: str,
        field_name: str,
        query: Optional[Dict[str, Any]] = None
    ) -> Optional[List[type[SQLModel]]]:
        """
        Retrieves records from the database based on a specific field value, with optional field limitations and additional query.

        Args:
            session (AsyncSession): The database session.
            data (str): The value to search for in the specified field.
            field_name (str): The name of the field to search in.
            query (dict, optional): Additional query criteria to further refine the search.

        Returns:
            list | None: The list of retrieved records as dictionaries, or None if no records are found.
        """
        filters = [getattr(self.model, field_name) == data]

        if query:
            filters.extend([
                getattr(self.model, key) == value
                for key, value in query.items()
                if hasattr(self.model, key)
            ])

        statement = select(self.model).where(*filters)
        result = await session.exec(statement)
        records = result.all()

        return records if records else None
    
    async def get_all(
        self,
        session: AsyncSession,
        query: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        search_in: Optional[List[str]] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves all records from the database based on various query, pagination, sorting, and field limitations.

        Args:
            session (AsyncSession): The database session.
            query (dict, optional): The query criteria for querying the collection.
            search (str, optional): A string to search for in the search_in fields.
            search_in (list, optional): A list of fields to search in if a search query is provided.
            page (int, optional): The page number for pagination.
            limit (int, optional): The number of documents per page.
            sort_by (str, optional): The field name to sort the results by.
            order_by (str, optional): The order to sort the results, either "asc" for ascending or "desc" for descending.

        Returns:
            dict: A dictionary containing the results, total number of items, total pages, and records per page.
        """
        filters = []

        # Apply query filters
        if query:
            filters.extend([
                getattr(self.model, key) == value
                for key, value in query.items()
                if hasattr(self.model, key)
            ])


        # Apply search filters
        if search and search_in:
            search_conditions = [
                getattr(self.model, field).ilike(f"%{search}%")
                for field in search_in if hasattr(self.model, field)
            ]
            if search_conditions:
                filters.append(func.or_(*search_conditions))

        # Build the base select statement
        statement = select(self.model).where(*filters)

        # Apply sorting
        if sort_by and hasattr(self.model, sort_by):
            order_func = desc if order_by == "desc" else asc
            statement = statement.order_by(order_func(getattr(self.model, sort_by)))

        # Count total records
        count_statement = select(func.count()).select_from(self.model).where(*filters)
        total_records = await session.scalar(count_statement)

        # Apply pagination
        if page and limit:
            offset = (page - 1) * limit
            statement = statement.offset(offset).limit(limit)

        # Execute the query
        result = await session.exec(statement)
        records = result.all()

        # Calculate pagination details
        total_pages = math.ceil(total_records / limit) if limit else 1

        return {
            "records_per_page": len(records),
            "total_items": total_records,
            "total_page": total_pages,
            "results": records
        }