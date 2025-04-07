// Consistify_App.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

import tkinter as tk
from tkinter import ttk

class ConsistifyApp(tk.Tk) :
    def __init__(self) :
    super().__init__()
    self.title("Consistify: Smart Reminder & Task Manager")
    self.geometry("800x600")

    # Create a Notebook widget for tabbed interface
    notebook = ttk.Notebook(self)
    notebook.pack(expand = True, fill = 'both')

    # Create frames for each tab
    self.home_frame = ttk.Frame(notebook)
    self.task_detail_frame = ttk.Frame(notebook)
    self.notifications_frame = ttk.Frame(notebook)
    self.settings_frame = ttk.Frame(notebook)

    # Add frames to the notebook with tab labels
    notebook.add(self.home_frame, text = 'Home')
    notebook.add(self.task_detail_frame, text = 'Task Detail')
    notebook.add(self.notifications_frame, text = 'Notifications')
    notebook.add(self.settings_frame, text = 'Settings')

    self.create_home_ui()
    self.create_task_detail_ui()
    self.create_notifications_ui()
    self.create_settings_ui()

    def create_home_ui(self) :
    # Home tab content
    label = ttk.Label(self.home_frame, text = "Welcome to Consistify! Here are your tasks:")
    label.pack(pady = 10)

    # Listbox to display tasks
    self.task_listbox = tk.Listbox(self.home_frame)
    self.task_listbox.pack(expand = True, fill = 'both', padx = 10, pady = 10)

    # Add sample tasks
    sample_tasks = [
        "Task 1: Check email",
            "Task 2: Gym - Chest workout",
            "Task 3: Meeting at 3PM"
    ]
    for task in sample_tasks:
        self.task_listbox.insert(tk.END, task)

            def create_task_detail_ui(self) :
            # Task Detail tab content
            label = ttk.Label(self.task_detail_frame, text = "Task Details:")
            label.pack(pady = 10)

            # Text widget for detailed task information
            self.detail_text = tk.Text(self.task_detail_frame, height = 15)
            self.detail_text.pack(expand = True, fill = 'both', padx = 10, pady = 10)
            self.detail_text.insert(tk.END, "Select a task from the Home tab to see details here.")

            def create_notifications_ui(self) :
            # Notifications tab content
            label = ttk.Label(self.notifications_frame, text = "Notifications:")
            label.pack(pady = 10)

            # Listbox to display notifications
            self.notification_listbox = tk.Listbox(self.notifications_frame)
            self.notification_listbox.pack(expand = True, fill = 'both', padx = 10, pady = 10)

            # Add sample notifications
            sample_notifications = [
                "Reminder: Task 2 is due soon.",
                    "Reminder: Task 3 in 30 minutes."
            ]
            for note in sample_notifications :
                self.notification_listbox.insert(tk.END, note)

                    def create_settings_ui(self) :
                    # Settings tab content
                    label = ttk.Label(self.settings_frame, text = "Settings:")
                    label.pack(pady = 10)

                    # Example setting : Reminder Frequency
                    reminder_label = ttk.Label(self.settings_frame, text = "Reminder Frequency (minutes):")
                    reminder_label.pack(pady = 5)
                    self.reminder_freq_entry = ttk.Entry(self.settings_frame)
                    self.reminder_freq_entry.pack(pady = 5)

                    # Save button for settings
                    save_button = ttk.Button(self.settings_frame, text = "Save Settings", command = self.save_settings)
                    save_button.pack(pady = 20)

                    def save_settings(self) :
                    freq = self.reminder_freq_entry.get()
                    print("Settings saved. Reminder Frequency:", freq)

                    if __name__ == "__main__" :
                        app = ConsistifyApp()
                        app.mainloop()
