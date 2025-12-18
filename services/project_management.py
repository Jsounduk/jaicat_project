# services/project_management.py

class ProjectManagement:
    def __init__(self):
        self.projects = {}

    def create_project(self, project_name):
        """Create a new project."""
        if project_name not in self.projects:
            self.projects[project_name] = {"tasks": [], "status": "ongoing"}
            return f"Project '{project_name}' created."
        else:
            return f"Project '{project_name}' already exists."

    def add_task(self, project_name, task):
        """Add a task to a project."""
        if project_name in self.projects:
            self.projects[project_name]["tasks"].append(task)
            return f"Task '{task}' added to project '{project_name}'."
        else:
            return f"Project '{project_name}' does not exist."

    def list_projects(self):
        """List all projects and their tasks."""
        if not self.projects:
            return "No projects available."
        project_list = ""
        for project_name, details in self.projects.items():
            tasks = ', '.join(details["tasks"]) if details["tasks"] else "No tasks."
            project_list += f"Project: {project_name}, Status: {details['status']}, Tasks: {tasks}\n"
        return project_list.strip()

    def complete_project(self, project_name):
        """Mark a project as completed."""
        if project_name in self.projects:
            self.projects[project_name]["status"] = "completed"
            return f"Project '{project_name}' marked as completed."
        else:
            return f"Project '{project_name}' does not exist."
