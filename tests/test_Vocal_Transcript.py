import pytest
from src.Vocal_Transcript import transcribe_from_microphone

def test_transcribe_from_microphone_success():
    result = {
        "text": "Bonjour",
        "status": "success",
        "status_code": 200
    }
    assert result["status"] == "success"
    assert isinstance(result["text"], str)
    assert result["status_code"] == 200

def test_transcribe_from_microphone_no_speech():
    result = {
        "text": None,
        "status": "speech could not be recognized",
        "status_code": 204
    }
    assert result["status"] == "speech could not be recognized"
    assert result["text"] is None
    assert result["status_code"] == 204

def test_transcribe_from_microphone_error():
    result = {
        "text": None,
        "status": "Canceled: Error during speech recognition",
        "status_code": 500
    }
    assert result["status"] == "Canceled: Error during speech recognition"
    assert result["text"] is None
    assert result["status_code"] == 500

def test_transcribe_from_microphone_no_input():
    result = {
        "text": None,
        "status": "Canceled: No speech input",
        "status_code": 400
    }
    assert result["status"] == "Canceled: No speech input"
    assert result["text"] is None
    assert result["status_code"] == 400

def test_transcribe_from_microphone_unknown_error():
    result = {
        "text": None,
        "status": "Unknown error",
        "status_code": 500
    }
    assert result["status"] == "Unknown error"
    assert result["text"] is None
    assert result["status_code"] == 500

