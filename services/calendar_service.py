from datetime import datetime
import datetime

class CalendarService:
    def get_current_date(self):
        return datetime.now().strftime("%B %d, %Y")
