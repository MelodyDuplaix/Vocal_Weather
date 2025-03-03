import pytest
import requests
from src.Geolocation import get_geolocation

def test_get_geolocation_valid_location():
    location = "Paris"
    geolocation = get_geolocation(location)
    
    assert "latitude" in geolocation
    assert "longitude" in geolocation
    assert "city" in geolocation
    assert geolocation["status"] == "success"
    assert geolocation["latitude"] is not None
    assert geolocation["longitude"] is not None
    assert geolocation["city"] == "Paris"

def test_get_geolocation_invalid_location():
    location = "Blablaland"
    geolocation = get_geolocation(location)
    
    assert geolocation["latitude"] is None
    assert geolocation["longitude"] is None
    assert geolocation["city"] is None
    assert geolocation["status"] == "Localisation non trouvée"
