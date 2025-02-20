from datetime import datetime, timedelta


def days_number_choice(dates):
    """
    Choose the number of days to forecast based on the dates extracted from the text, between 1, 3, 7, 14 and 16 days.
    Or choose the days range to forecast based on the dates extracted from the text.

    Args:
        dates (list): The dates extracted from the text.
        
    Returns:
        int or list: The number of days to forecast or the days range to forecast.
    """
    if isinstance(dates, list):
        # Convert datetime.datetime objects to datetime.date
        dates = [date.date() if isinstance(date, datetime) else date for date in dates]
        
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
            # Calculate the number of days to forecast based on the date range
            max_date = max(dates)
            days_number = (max_date - datetime.now().date()).days
            
            if days_number <= 3:
                return 3
            elif days_number <= 7:
                return 7
            elif days_number <= 14:
                return 14
            elif days_number <= 16:
                return 16
            else:
                return 1
        
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