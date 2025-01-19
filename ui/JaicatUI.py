import tkinter as tk
import os
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
from services.email_service import EmailService
import json

class JaicatUI:
    def __init__(self, assistant):
        """Initialize the UI and connect it to the Jaicat assistant."""
        self.assistant = assistant
        self.window = tk.Tk()
        self.window.title("Jaicat - AI Assistant")
        self.window.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        """Set up the UI components."""
        # Email Management Section
        self.email_frame = tk.Frame(self.window)
        self.email_frame.pack(pady=10)

        self.select_email_button = tk.Button(
            self.email_frame, text="Select Email Account", command=self.select_email_account
        )
        self.select_email_button.pack()

        self.send_email_button = tk.Button(
            self.email_frame, text="Send Email", command=self.prepare_email_sending
        )
        self.send_email_button.pack()

        # Status Bar
        self.status_bar = tk.Label(self.window, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def select_email_account(self):
        """Display and allow selection of user email accounts."""
        user_file = f"user_data/{self.assistant.logged_in_user}.json"
        email_accounts = self.assistant.email_service.load_user_emails(user_file)

        if not email_accounts:
            messagebox.showerror("Error", "No email accounts found for this user.")
            return

        # Create a selection window
        selection_window = tk.Toplevel(self.window)
        selection_window.title("Select Email Account")

        # Listbox for displaying accounts
        email_listbox = tk.Listbox(selection_window, height=10, width=50)
        email_listbox.pack(pady=10)

        # Populate the listbox
        for idx, account in enumerate(email_accounts, start=1):
            email_listbox.insert(tk.END, f"{idx}- {account['address']}")

        def confirm_selection():
            try:
                selected_idx = email_listbox.curselection()[0]
                self.selected_email = email_accounts[selected_idx]
                messagebox.showinfo("Selection", f"Selected email: {self.selected_email['address']}")
                selection_window.destroy()
            except IndexError:
                messagebox.showerror("Error", "No email account selected.")

        # Confirmation button
        confirm_button = tk.Button(selection_window, text="Confirm", command=confirm_selection)
        confirm_button.pack(pady=10)

    def prepare_email_sending(self):
        """Open a dialog to input email details and send the email."""
        if not hasattr(self, "selected_email"):
            messagebox.showerror("Error", "Please select an email account first.")
            return

        # Input recipient
        recipient = simpledialog.askstring("Recipient", "Enter recipient's email:")
        if not recipient:
            return

        # Input subject
        subject = simpledialog.askstring("Subject", "Enter the subject:")
        if not subject:
            return

        # Input body
        body = simpledialog.askstring("Body", "Enter the email body:")
        if not body:
            return

        # Send the email
        response = self.assistant.email_service.send_email(
            from_email=self.selected_email,
            to_email=recipient,
            subject=subject,
            body=body,
        )
        messagebox.showinfo("Email Status", response)

    def run(self):
        """Run the main event loop for the GUI."""
        self.window.mainloop()


if __name__ == "__main__":
    # Mock assistant object with email_service
    class MockAssistant:
        def __init__(self):
            
            self.email_service = EmailService(encryption_key="your_encryption_key")
            self.logged_in_user = "example_user"

    assistant = MockAssistant()
    ui = JaicatUI(assistant)
    ui.run()
