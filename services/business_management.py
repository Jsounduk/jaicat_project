import json
import os
from datetime import datetime

class BusinessManagementService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(base_dir, "business_data.json")

    def initialize_data(self):
        """Initializes an empty structure for business management data."""
        data = {
            "projects": [],
            "finances": {"income": 0, "expenses": 0},
            "meetings": [],
            "performance": {"metrics": []}
        }
        with open(self.data_file, 'w') as file:
            json.dump(data, file, indent=4)
    
    def load_data(self):
        """Loads the current data from the JSON file."""
        with open(self.data_file, 'r') as file:
            return json.load(file)

    def save_data(self, data):
        """Saves the current data back to the JSON file."""
        with open(self.data_file, 'w') as file:
            json.dump(data, file, indent=4)

    def add_project(self, name, description, deadline):
        """Adds a new project to the system."""
        data = self.load_data()
        new_project = {
            "name": name,
            "description": description,
            "deadline": deadline,
            "status": "ongoing"
        }
        data['projects'].append(new_project)
        self.save_data(data)
        return f"Project '{name}' added successfully."

    def track_finances(self, income=None, expense=None):
        """Adds income or expenses to the financial tracker."""
        data = self.load_data()
        if income:
            data['finances']['income'] += income
        if expense:
            data['finances']['expenses'] += expense
        self.save_data(data)
        return f"Finances updated. Income: {data['finances']['income']}, Expenses: {data['finances']['expenses']}"

    def add_meeting(self, title, time, participants):
        """Schedules a meeting."""
        data = self.load_data()
        new_meeting = {
            "title": title,
            "time": time,
            "participants": participants
        }
        data['meetings'].append(new_meeting)
        self.save_data(data)
        return f"Meeting '{title}' scheduled successfully."

    def add_performance_metric(self, metric_name, value):
        """Adds a performance metric."""
        data = self.load_data()
        new_metric = {
            "metric": metric_name,
            "value": value,
            "date": datetime.now().isoformat()
        }
        data['performance']['metrics'].append(new_metric)
        self.save_data(data)
        return f"Performance metric '{metric_name}' added with value {value}."

    def get_summary(self):
        """Returns a summary of all business management activities."""
        data = self.load_data()
        summary = {
            "projects": data['projects'],
            "finances": data['finances'],
            "meetings": data['meetings'],
            "performance_metrics": data['performance']['metrics']
        }
        return summary


# Example usage
if __name__ == "__main__":
    bm_service = BusinessManagementService()
    
    # Add a project
    print(bm_service.add_project("Website Revamp", "Redesign the corporate website", "2024-12-01"))
    
    # Track finances
    print(bm_service.track_finances(income=5000))
    print(bm_service.track_finances(expense=1500))
    
    # Schedule a meeting
    print(bm_service.add_meeting("Marketing Strategy", "2024-10-10 10:00", ["John", "Jane", "Michael"]))
    
    # Add performance metric
    print(bm_service.add_performance_metric("Quarterly Sales", 20000))
    
    # Get summary
    summary = bm_service.get_summary()
    print(json.dumps(summary, indent=4))
