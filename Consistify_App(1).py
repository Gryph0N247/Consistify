import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkcalendar import Calendar
from datetime import datetime

class ConsistifyApp(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.title("Consistify: Smart Reminder & Task Manager")
        self.geometry("900x750")

        self.tasks = []

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create frames for the tabs: Home, Task Detail, and Calendar
        self.home_frame = ttk.Frame(notebook)
        self.task_detail_frame = ttk.Frame(notebook)
        self.calendar_frame = ttk.Frame(notebook)

        notebook.add(self.home_frame, text='Home')
        notebook.add(self.task_detail_frame, text='Task Detail')
        notebook.add(self.calendar_frame, text='Calendar')

        self.create_home_ui()
        self.create_task_detail_ui()
        self.create_calendar_ui()

    def create_home_ui(self):
        # Label for task list
        label = ttk.Label(self.home_frame, text="Your Tasks:")
        label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        # Listbox to display tasks
        self.task_listbox = tk.Listbox(self.home_frame, font=("Helvetica", 11))
        self.task_listbox.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
        self.task_listbox.bind("<<ListboxSelect>>", self.show_task_details)

        # Configure grid weights for proper resizing
        self.home_frame.rowconfigure(1, weight=1)
        self.home_frame.columnconfigure(0, weight=1)

        # Frame for adding tasks
        add_task_frame = ttk.LabelFrame(self.home_frame, text="Add New Task")
        add_task_frame.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        add_task_frame.columnconfigure(1, weight=1)

        # Input for task title
        title_label = ttk.Label(add_task_frame, text="Task Title:")
        title_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.title_entry = ttk.Entry(add_task_frame, font=("Helvetica", 11))
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Input for task description
        desc_label = ttk.Label(add_task_frame, text="Description:")
        desc_label.grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        self.desc_text = tk.Text(add_task_frame, height=4, font=("Helvetica", 11))
        self.desc_text.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Reminder Schedule Section
        schedule_label = ttk.Label(add_task_frame, text="Reminder Schedule:")
        schedule_label.grid(row=2, column=0, padx=5, pady=(10,5), sticky='w')
        
        # Create a frame for the schedule inputs
        schedule_frame = ttk.Frame(add_task_frame)
        schedule_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Lists to hold day checkbuttons, time entries, and AM/PM selectors
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.day_vars = {}
        self.day_time_entries = {}
        self.day_ampm_vars = {}

        for i, day in enumerate(self.days):
            var = tk.BooleanVar()
            self.day_vars[day] = var
            chk = ttk.Checkbutton(schedule_frame, text=day, variable=var)
            chk.grid(row=i, column=0, padx=5, pady=2, sticky='w')
            
            # Entry for time
            time_entry = ttk.Entry(schedule_frame, width=10, font=("Helvetica", 11))
            time_entry.grid(row=i, column=1, padx=5, pady=2, sticky='w')
            time_entry.insert(0, "HH:MM")  # Placeholder text
            self.day_time_entries[day] = time_entry

            # AM/PM selector using a Combobox
            ampm_var = tk.StringVar(value="AM")
            self.day_ampm_vars[day] = ampm_var
            ampm_combo = ttk.Combobox(schedule_frame, textvariable=ampm_var, values=["AM", "PM"], width=5, font=("Helvetica", 11))
            ampm_combo.grid(row=i, column=2, padx=5, pady=2, sticky='w')

        # Button to add task
        add_button = ttk.Button(add_task_frame, text="Add Task", command=self.add_task)
        add_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

    def create_task_detail_ui(self):
        label = ttk.Label(self.task_detail_frame, text="Task Details:")
        label.pack(pady=10, padx=10, anchor='w')
        self.detail_text = tk.Text(self.task_detail_frame, height=30, font=("Helvetica", 11))
        self.detail_text.pack(expand=True, fill='both', padx=10, pady=10)
        self.detail_text.insert(tk.END, "Select a task from the Home tab to see details here.")

    def create_calendar_ui(self):
        # Calendar tab: Create a Calendar widget and a listbox for tasks
        calendar_label = ttk.Label(self.calendar_frame, text="Calendar:")
        calendar_label.pack(pady=5, padx=10, anchor='w')
        
        # Create a frame to hold the calendar and task list side-by-side
        cal_frame = ttk.Frame(self.calendar_frame)
        cal_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Calendar widget from tkcalendar
        self.calendar = Calendar(cal_frame, selectmode='day')
        self.calendar.grid(row=0, column=0, padx=10, pady=10)
        self.calendar.bind("<<CalendarSelected>>", self.update_calendar_tasks)

        # Listbox to display tasks for the selected day
        self.calendar_task_listbox = tk.Listbox(cal_frame, font=("Helvetica", 11), width=40)
        self.calendar_task_listbox.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        # Configure grid weights
        cal_frame.columnconfigure(0, weight=1)
        cal_frame.columnconfigure(1, weight=1)
        cal_frame.rowconfigure(0, weight=1)

    def add_task(self):
        title = self.title_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        # Build reminder schedule from selected days
        reminder_schedule = {}
        for day in self.days:
            if self.day_vars[day].get():
                time_str = self.day_time_entries[day].get().strip()
                ampm = self.day_ampm_vars[day].get().strip()
                full_time = f"{time_str} {ampm}"
                reminder_schedule[day] = full_time

        if title:
            task = {"title": title, "description": description, "reminder_schedule": reminder_schedule}
            self.tasks.append(task)
            self.task_listbox.insert(tk.END, title)
            # Clear inputs
            self.title_entry.delete(0, tk.END)
            self.desc_text.delete("1.0", tk.END)
            for day in self.days:
                self.day_vars[day].set(False)
                self.day_time_entries[day].delete(0, tk.END)
                self.day_time_entries[day].insert(0, "HH:MM")
                self.day_ampm_vars[day].set("AM")
            # Update calendar tasks in case the new task applies to the selected date
            self.update_calendar_tasks()
        else:
            print("Task title is required.")

    def show_task_details(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            task = self.tasks[index]
            self.detail_text.delete("1.0", tk.END)
            details = f"Title: {task['title']}\n\nDescription:\n{task['description']}\n\nReminder Schedule:\n"
            for day, time_str in task['reminder_schedule'].items():
                details += f"{day}: {time_str}\n"
            self.detail_text.insert(tk.END, details)
        else:
            self.detail_text.delete("1.0", tk.END)
            self.detail_text.insert(tk.END, "Select a task from the Home tab to see details here.")

    def update_calendar_tasks(self, event=None):
        # Clear the listbox
        self.calendar_task_listbox.delete(0, tk.END)
        # Get the selected date from the calendar
        selected_date = self.calendar.selection_get()
        day_name = selected_date.strftime("%A")
        # Find tasks scheduled for the selected day
        for task in self.tasks:
            if day_name in task["reminder_schedule"]:
                time_str = task["reminder_schedule"][day_name]
                display_text = f"{task['title']} at {time_str}"
                self.calendar_task_listbox.insert(tk.END, display_text)

if __name__ == "__main__":
    app = ConsistifyApp()
    app.mainloop()
