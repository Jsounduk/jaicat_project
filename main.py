# main.py — Launch JaicatUI with the new DI bootstrap
from app.bootstrap import build_controller
from ui.JaicatUI import launch_ui

if __name__ == "__main__":
    controller = build_controller()
    launch_ui(controller)
    # Example usage of EmailService
    
