import pytest
from datetime import datetime
from src.Entities_Extract import load_model, extract_entities

def test_load_model():
    ner_pipeline = load_model()
    assert ner_pipeline is not None
    assert callable(ner_pipeline)
    
def test_extract_entities_valid_text():
    text = "Je vais à Paris demain à 14h."
    ner_pipeline = load_model()
    entities = extract_entities(text, ner_pipeline)

    assert "date" in entities
    assert "localisation" in entities
    assert isinstance(entities["date"], list)
    assert isinstance(entities["localisation"], list)
    assert len(entities["date"]) > 0
    assert len(entities["localisation"]) > 0
    assert isinstance(entities["date"][0], datetime)
    assert "Paris" in entities["localisation"]

def test_extract_entities_no_entities():
    text = "Ceci est un texte sans date ni localisation."
    ner_pipeline = load_model()
    entities = extract_entities(text, ner_pipeline)

    assert "date" in entities
    assert "localisation" in entities
    assert len(entities["date"]) == 0
    assert len(entities["localisation"]) == 0

def test_extract_entities_invalid_text_format():
    text = 12345  # Not a string
    ner_pipeline = load_model()
    entities = extract_entities(text, ner_pipeline)

    assert "date" in entities
    assert "localisation" in entities
    assert len(entities["date"]) == 0
    assert len(entities["localisation"]) == 0

def test_extract_entities_multiple_dates_and_locations():
    text = "Je vais à Paris le 5 mai et à Lyon le 10 juin."
    ner_pipeline = load_model()
    entities = extract_entities(text, ner_pipeline)

    assert "date" in entities
    assert "localisation" in entities
    assert len(entities["date"]) == 2
    assert len(entities["localisation"]) == 2
    assert "Paris" in entities["localisation"]
    assert "Lyon" in entities["localisation"]
    assert isinstance(entities["date"][0], datetime)
    assert isinstance(entities["date"][1], datetime)

def test_extract_entities_date_parsing():
    text = "Rendez-vous le 25 décembre."
    ner_pipeline = load_model()
    entities = extract_entities(text, ner_pipeline)

    assert "date" in entities
    assert len(entities["date"]) > 0
    assert isinstance(entities["date"][0], datetime)
    assert entities["date"][0].month == 12
    assert entities["date"][0].day == 25

