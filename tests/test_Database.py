import pytest
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from src.Database import create_connexion, create_table, insert_data 

load_dotenv()
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

@pytest.fixture
def setup_database():
    """Crée une base de test et retourne l'engine et la table."""
    engine, LogTable = create_table()
    yield engine, LogTable
    engine.dispose()

@pytest.fixture
def setup_connection():
    """Crée une connexion à la base et retourne l'engine et la table."""
    engine, LogTable = create_connexion()
    yield engine, LogTable
    engine.dispose()

def test_create_connexion(setup_connection):
    """Teste la création de la connexion à la base."""
    engine, LogTable = setup_connection
    assert engine is not None
    assert LogTable is not None

def test_create_table(setup_database):
    """Teste la création de la table."""
    engine, _ = setup_database
    inspector = inspect(engine)
    assert "log_table" in inspector.get_table_names()

def test_insert_data(setup_database):
    """Teste l'insertion de données."""
    engine, LogTable = setup_database
    test_data = {
        "timestamp": "2025-03-03T12:00:00",
        "code_stt": 200,
        "error_message": None,
        "original_text": "Test weather data",
        "db_connexion_time": 100,
        "response_time_azure": 150,
        "recognized_entities": "entity1, entity2",
        "extraction_time_entities": 50,
        "formatted_dates": "2025-03-03",
        "localisation": "Paris",
        "weather_api_code": 200,
        "weather_api_time": 120,
        "weather_api_response": "Sunny",
        "weather": "Clear"
    }

    # Insère les données
    insert_data(engine, test_data, LogTable)
    
    # Crée une nouvelle session pour interroger la base
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Attend quelques secondes pour que la donnée soit bien insérée
    record = session.query(LogTable).filter_by(original_text="Test weather data").first()
    session.close()

    # Vérifie que l'enregistrement a bien été inséré
    assert record is not None, "L'enregistrement n'a pas été inséré."
    assert record.original_text == "Test weather data", f"Valeur incorrecte pour original_text : {record.original_text}"
    assert record.code_stt == 200, f"Valeur incorrecte pour code_stt : {record.code_stt}"
