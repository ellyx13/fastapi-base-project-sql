from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.value import UserRoles
from db.engine import db_engine

class CommonsDependencies:
    """
    Handles common dependencies extracted from the request.

    This class is used to extract and store common dependencies such as the current user, user type,
    and whether the request is from a public API, from the FastAPI request object.

    If it is a public api, then user_id, user_type will have the value None and is_public_api will be True and vice versa.

    Args:
        request (Request): The FastAPI request object containing the payload.

    Attributes:
        current_user (str, None): The ID of the current user extracted from the request payload.
        user_type (str, None): The type of the current user (e.g., admin, customer) extracted from the request payload.
        is_public_api (bool, None): Indicates whether the request is from a public API, extracted from the request payload.
    """

    def __init__(self, request: Request = None, session: AsyncSession = Depends(db_engine.get_session)) -> None:
        self.session = session
        self.current_user = None
        self.user_type = None
        self.is_public_api = None
        if request:
            self.api_path = request.url.path
            self.headers = dict(request.headers)
            if hasattr(request.state, "payload"):
                self.current_user = request.state.payload.get("user_id")
                self.user_type = request.state.payload.get("user_type")
                self.is_public_api = request.state.payload.get("is_public_api")

    def is_admin(self) -> bool:
        """
        Checks if the current user is an admin.

        Returns:
            bool: True if the current user is an admin, False otherwise.
        """
        return self.user_type == UserRoles.ADMIN.value if self.user_type else False
    
    @classmethod
    def from_session(cls, session: AsyncSession):
        return cls(request=None, session=session)