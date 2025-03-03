import pytest
from datetime import datetime, timedelta
from src.Days_Choice import days_number_choice


def get_today():
    return datetime.now().date()

def test_single_today():
    today = get_today()
    result = days_number_choice([today])
    assert result == 1 

def test_single_within_2_days():
    today = get_today()
    date_in_2_days = today + timedelta(days=2)
    result = days_number_choice([date_in_2_days])
    assert result == 3  

def test_single_within_7_days():
    today = get_today()
    date_in_6_days = today + timedelta(days=6)
    result = days_number_choice([date_in_6_days])
    assert result == 7

def test_single_within_14_days():
    today = get_today()
    date_in_13_days = today + timedelta(days=13)
    result = days_number_choice([date_in_13_days])
    assert result == 14

def test_single_within_16_days():
    today = get_today()
    date_in_15_days = today + timedelta(days=15)
    result = days_number_choice([date_in_15_days])
    assert result == 16 

def test_single_over_16_days():
    today = get_today()
    date_in_20_days = today + timedelta(days=20)
    result = days_number_choice([date_in_20_days])
    assert result == 1 

def test_multiple_dates_within_range():
    today = get_today()
    date_in_3_days = today + timedelta(days=3)
    date_in_5_days = today + timedelta(days=5)
    result = days_number_choice([date_in_3_days, date_in_5_days])
    assert result == 7 

def test_multiple_dates_with_far_date():
    today = get_today()
    date_in_3_days = today + timedelta(days=3)
    date_in_20_days = today + timedelta(days=20)
    result = days_number_choice([date_in_3_days, date_in_20_days])
    assert result == 1  

def test_multiple_dates_within_16_days():
    today = get_today()
    date_in_13_days = today + timedelta(days=13)
    date_in_14_days = today + timedelta(days=14)
    result = days_number_choice([date_in_13_days, date_in_14_days])
    assert result == 16 

def test_multiple_dates_range():
    today = get_today()
    date_in_2_days = today + timedelta(days=2)
    date_in_10_days = today + timedelta(days=10)
    result = days_number_choice([date_in_2_days, date_in_10_days])
    assert result == 14  

def test_empty_list():
    result = days_number_choice([])
    assert result == 1

def test_past_dates():
    today = get_today()
    date_in_past = today - timedelta(days=1)
    result = days_number_choice([date_in_past])
    assert result == 1

