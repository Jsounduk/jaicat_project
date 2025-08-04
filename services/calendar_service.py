import datetime

class CalendarService:
    def get_current_date(self):
        return datetime.datetime.now().strftime("%B %d, %Y")
