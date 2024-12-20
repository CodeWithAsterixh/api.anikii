from datetime import datetime, timedelta

# Get the current year
this_year = datetime.now().year

class ThisWhen:
    def __init__(self, date: datetime = None):
        if date is None:
            date = datetime.now()
        self.month = date.month
        self.day = date.day
        self.year = date.year

this_when = ThisWhen()
def get_days_difference(length: int = 7, this_when: ThisWhen = ThisWhen()) -> str:
    current_date = datetime(this_when.year, this_when.month, this_when.day)
    past_date = current_date - timedelta(days=length)

    yymmdd = past_date.strftime("%Y%m%d")
    return yymmdd

# Seasons: WINTER, SPRING, FALL, SUMMER
def get_current_season() -> str:
    now = datetime.now()
    month = now.month  # 1-indexed: 1 = January, 12 = December

    if month == 12 or month <= 2:
        return "WINTER"
    elif 3 <= month <= 5:
        return "SPRING"
    elif 6 <= month <= 8:
        return "SUMMER"
    elif 9 <= month <= 11:
        return "FALL"
    else:
        return "SUMMER"

available_seasons = ["FALL", "SPRING", "SUMMER", "WINTER"]


def get_years(year1=1999, year2=None):
    if year2 is None:
        year2 = datetime.now().year  # Get the current year if year2 is not provided
    return list(range(year1, year2 + 1))

