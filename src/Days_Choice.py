
from datetime import datetime, timedelta


def days_number_choice(dates):
    """
    Choose the number of days to forecast based on the dates extracted from the text, between 1, 3, 7, 14 and 16 days.
    Or choose the days range to forecast based on the dates extracted from the text.

    Args:
        dates (list): The dates extracted from the text.
    """
    if isinstance(dates, list):
        if len(dates) == 1:
            if dates[0] == datetime.now().date():
                days_number = 1
            elif dates[0] > datetime.now().date() and dates[0] <= datetime.now().date() + timedelta(days=3):
                days_number = 3
            elif dates[0] > datetime.now().date() and dates[0] <= datetime.now().date() + timedelta(days=7):
                days_number = 7
            elif dates[0] > datetime.now().date() and dates[0] <= datetime.now().date() + timedelta(days=14):
                days_number = 14
            elif dates[0] > datetime.now().date() and dates[0] <= datetime.now().date() + timedelta(days=16):
                days_number = 16
            else:
                days_number = 1
            return days_number
        else:
            if len(dates) == 2:
                days_range = sorted(dates)
            else:
                days_range = [min(dates), max(dates)]
            return days_range
        
if __name__ == "__main__":
    dates = [datetime.now().date() + timedelta(days=3)]
    days_number = days_number_choice(dates)
    print(days_number)
    dates = [datetime.now().date(), datetime.now().date() + timedelta(days=3)]
    days_range = days_number_choice(dates)
    print(days_range)
    dates = [datetime.now().date(), datetime.now().date() - timedelta(days=2), datetime.now().date() + timedelta(days=7)]
    days_range = days_number_choice(dates)
    print(days_range)