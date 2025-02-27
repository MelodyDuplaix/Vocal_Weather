from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
    
def create_connexion():
    """
    Creates a database engine and a logble table for connection to the database.

    Returns:
        (engine, LogTable): A tupple containing The database engine and the LogTable.
    """
    metadata = MetaData()
    Base = declarative_base(metadata=metadata)
    class LogTable(Base):
        __tablename__ = 'log_table'
        id = Column(Integer, primary_key=True, autoincrement=True)
        timestamp = Column(String, nullable=False)
        code_stt = Column(Integer, nullable=False)
        error_message = Column(String, nullable=True)
        original_text = Column(String, nullable=False)
        db_connexion_time = Column(Integer, nullable=False)
        response_time_azure = Column(Integer, nullable=False)
        recognized_entities = Column(String, nullable=True)
        extraction_time_entities = Column(Integer, nullable=False)
        formatted_dates = Column(String, nullable=True)
        localisation = Column(String, nullable=True)
        weather_api_code = Column(Integer, nullable=False)
        weather_api_time = Column(Integer, nullable=False)
        weather_api_response = Column(String, nullable=True)
        weather = Column(String, nullable=True)
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    return engine, LogTable

def create_table():
    """
    Creates a database engine and a logble table for connection to the database.

    Returns:
        tuple: (engine, LogTable) - A tupple containing The database engine and the LogTable.
    """
    metadata = MetaData()
    Base = declarative_base(metadata=metadata)

    class LogTable(Base):
        __tablename__ = 'log_table'
        id = Column(Integer, primary_key=True, autoincrement=True)
        timestamp = Column(String, nullable=False)
        code_stt = Column(Integer, nullable=False)
        error_message = Column(String, nullable=True)
        original_text = Column(String, nullable=False)
        db_connexion_time = Column(Integer, nullable=False)
        response_time_azure = Column(Integer, nullable=False)
        recognized_entities = Column(String, nullable=True)
        extraction_time_entities = Column(Integer, nullable=False)
        formatted_dates = Column(String, nullable=True)
        localisation = Column(String, nullable=True)
        weather_api_code = Column(Integer, nullable=False)
        weather_api_time = Column(Integer, nullable=False)
        weather_api_response = Column(String, nullable=True)
        weather = Column(String, nullable=True)

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    
    # Check if the table already exists
    inspector = inspect(engine)
    if not inspector.has_table("log_table"):
        Base.metadata.create_all(engine)
        print("Table 'log_table' created successfully.")
    else:
        print("Table 'log_table' already exists.")

    return engine, LogTable
    
    
def insert_data(engine, data, LogTable):
    """
    Insert data into the LogTable table.

    Args:
        engine (engine): The database engine.
        data (dict): The data to insert.
        LogTable (LogTable): The LogTable object.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    new_record = LogTable(**data)
    session.add(new_record)
    session.commit()
    session.close()