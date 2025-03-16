from sqlmodel import SQLModel, create_engine
from .config import settings

class Engine(object):
    def __init__(self, database_url) -> None:
        self.database_url = database_url
        self.db_engine = create_engine(database_url)
        
    def create_db_and_tables(self):  
        SQLModel.metadata.create_all(self.db_engine)  

    def __new__(cls, database_url):
        if not hasattr(cls, "instance"):
            cls.instance = super(Engine, cls).__new__(cls)
        return cls.instance


app_engine = Engine(database_url=settings.database_url)
