from datetime import datetime
from typing import Annotated

from fastapi import Query, Request
from pydantic.functional_validators import AfterValidator
from utils import validator
from utils.value import OrderBy, UserRoles

from .exceptions import CoreErrorCode

class PaginationParams:
    """
    Handles pagination parameters extracted from the request query parameters.

    This class is used to extract and store parameters related to pagination, searching, sorting,
    and field selection from the FastAPI request object.

    Args:
        request (Request): The FastAPI request object containing query parameters.
        search (str, optional): A search string for filtering results. Defaults to None.
        page (int, optional): The page number for pagination, must be greater than 0. Defaults to 1.
        limit (int, optional): The number of records per page, must be greater than 0. Defaults to 20.
        fields (str, optional): A comma-separated list of fields to include in the response. Defaults to None.
        sort_by (str, optional): The field by which to sort the results. Defaults to "created_at".
        order_by (OrderBy, optional): The order in which to sort the results, either ascending or descending. Defaults to descending.

    Attributes:
        query (dict): A dictionary of query parameters extracted from the request.
        search (str): The search string.
        page (int): The page number for pagination.
        limit (int): The number of records per page.
        fields (str): The fields to include in the response.
        sort_by (str): The field by which to sort the results.
        order_by (OrderBy): The order in which to sort the results.
    """

    def __init__(
        self,
        request: Request,
        search: str = Query(None, description="Anything you want"),
        page: int = Query(default=1, gt=0),
        limit: int = Query(default=20, gt=0),
        sort_by: str = Query("created_at", description="Anything you want"),
        order_by: OrderBy = Query(OrderBy.DECREASE.value, description="desc: Descending | asc: Ascending"),
    ):
        self.query = dict(request.query_params)
        self.search = search
        self.page = page
        self.limit = limit
        self.sort_by = sort_by
        self.order_by = order_by

def check_email(value: str) -> str:
    """
    Validates whether a given string is a valid email address.

    Args:
        value (str): The string to validate as an email address.

    Returns:
        str: The validated email address string.

    Raises:
        CoreErrorCode.InvalidEmail: If the string is not a valid email address.
    """
    if validator.check_email(email=value):
        return value
    raise CoreErrorCode.InvalidEmail(email=value)


def check_phone(value: str) -> str:
    """
    Validates whether a given string is a valid phone number.

    Args:
        value (str): The string to validate as a phone number.

    Returns:
        str: The validated phone number string.

    Raises:
        CoreErrorCode.InvalidPhone: If the string is not a valid phone number.
    """
    if validator.check_phone(phone=value):
        return value
    raise CoreErrorCode.InvalidPhone(phone=value)


def check_date_format(value: str) -> str:
    """
    Validates whether a given string matches the date format "%Y-%m-%d".

    Args:
        value (str): The string to validate as a date.

    Returns:
        str: The validated date string.

    Raises:
        CoreErrorCode.InvalidDate: If the string does not match the date format "%Y-%m-%d".

    """
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise CoreErrorCode.InvalidDate(date=value)


EmailStr = Annotated[str, AfterValidator(check_email)]
PhoneStr = Annotated[str, AfterValidator(check_phone)]
DateStr = Annotated[str, AfterValidator(check_date_format)]
