from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

class Engine(object):
    def __init__(self, database_url) -> None:
        self.database_url = database_url
        self.db_engine = create_async_engine(self.database_url, echo=True, future=True)
        self.async_session = sessionmaker(self.db_engine, class_=AsyncSession, expire_on_commit=False)

        
    async def create_db_and_tables(self):  
        async with self.db_engine.begin() as engine:
            await engine.run_sync(SQLModel.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        async with self.async_session() as session:
            yield session
        
    def __new__(cls, database_url):
        if not hasattr(cls, "instance"):
            cls.instance = super(Engine, cls).__new__(cls)
        return cls.instance


db_engine = Engine(database_url=settings.database_url)
