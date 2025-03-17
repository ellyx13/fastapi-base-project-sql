from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ownership_field: str = "created_by"
    fields_not_modified: list[str] = ["updated_at", "updated_by"]

settings = Settings()
