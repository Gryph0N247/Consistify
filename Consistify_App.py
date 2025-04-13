# ------------------------------ MODULE IMPORTS ------------------------------
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from datetime import datetime, date
import calendar

# ------------------------------ CLASS INITIALIZATION ------------------------------
class ConsistifyApp(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.title("Consistify: Smart Reminder & Task Manager")
        self.geometry("900x750")
        self.tasks = []

        # Set up current month/year for the custom calendar view
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month

        # Create two tabs: Home and Calendar
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # ------------------------------ CREATE TABS ------------------------------
        self.home_frame = ttk.Frame(notebook)
        self.calendar_frame = ttk.Frame(notebook)

        notebook.add(self.home_frame, text='Home')
        notebook.add(self.calendar_frame, text='Calendar')

        # Initialize each tab
        self.create_home_ui()
        self.create_calendar_ui()

    # ------------------------------ HOME TAB ------------------------------
    def create_home_ui(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=60, font=("Helvetica", 12))

        # Label for the Home tab
        label = ttk.Label(self.home_frame, text="Your Tasks:", font=("Helvetica", 14))
        label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        # Two columns: Task Title and Schedule summary
        self.task_tree = ttk.Treeview(self.home_frame, columns=("title", "schedule"), show='headings')
        self.task_tree.heading("title", text="Task Title", anchor='center')
        self.task_tree.heading("schedule", text="Schedule", anchor='center')
        self.task_tree.column("title", anchor="center", width=400)
        self.task_tree.column("schedule", anchor="center", width=400)
        self.task_tree.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
        self.task_tree.bind("<Double-1>", self.on_double_click)

        # Add New Task button
        btn_style = ttk.Style()
        btn_style.configure("Big.TButton", font=("Helvetica", 16), padding=10)
        add_task_btn = ttk.Button(self.home_frame, text="Add New Task", command=self.open_add_task_window, style="Big.TButton")
        add_task_btn.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

        # Grid configuration
        self.home_frame.rowconfigure(1, weight=1)
        self.home_frame.columnconfigure(0, weight=1)

    # ------------------------------ DOUBLE-CLICK HANDLER ------------------------------
    # When a task is double-clicked in the Home tab, open the Edit Task window
    def on_double_click(self, event):
        selected = self.task_tree.selection()
        if selected:
            item_id = selected[0]
            index = int(item_id)
            self.open_edit_task_window(index)

    # ------------------------------ TASK CREATION WINDOW ------------------------------
    # Opens a new window that lets the user enter a new task
    def open_add_task_window(self):
        add_window = tk.Toplevel(self)
        add_window.title("Add New Task")
        add_window.geometry("500x600")
        
        form_frame = ttk.Frame(add_window, padding=10)
        form_frame.pack(expand=True, fill='both')

        # Task Title
        title_label = ttk.Label(form_frame, text="Task Title:")
        title_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        title_entry = ttk.Entry(form_frame, font=("Helvetica", 11))
        title_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Task Description
        desc_label = ttk.Label(form_frame, text="Description:")
        desc_label.grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        desc_text = tk.Text(form_frame, height=4, font=("Helvetica", 11))
        desc_text.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Reminder Schedule Section
        schedule_label = ttk.Label(form_frame, text="Reminder Schedule:")
        schedule_label.grid(row=2, column=0, padx=5, pady=(10,5), sticky='w')

        schedule_frame = ttk.Frame(form_frame)
        schedule_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_vars = {}
        day_time_entries = {}
        day_ampm_vars = {}

        for i, day in enumerate(days):
            var = tk.BooleanVar()
            day_vars[day] = var
            chk = ttk.Checkbutton(schedule_frame, text=day, variable=var)
            chk.grid(row=i, column=0, padx=5, pady=2, sticky='w')

            time_entry = ttk.Entry(schedule_frame, width=10, font=("Helvetica", 11))
            time_entry.grid(row=i, column=1, padx=5, pady=2, sticky='w')
            time_entry.insert(0, "HH:MM")
            day_time_entries[day] = time_entry

            ampm_var = tk.StringVar(value="AM")
            day_ampm_vars[day] = ampm_var
            ampm_combo = ttk.Combobox(schedule_frame, textvariable=ampm_var, values=["AM", "PM"], width=5, font=("Helvetica", 11))
            ampm_combo.grid(row=i, column=2, padx=5, pady=2, sticky='w')

        # Submit button
        submit_btn = ttk.Button(form_frame, text="Submit Task",
                                command=lambda: self.handle_add_task(title_entry, desc_text, day_vars, day_time_entries, day_ampm_vars, add_window))
        submit_btn.grid(row=4, column=0, columnspan=2, padx=5, pady=20)

        form_frame.columnconfigure(1, weight=1)

    # ------------------------------ TASK HANDLING FUNCTION ------------------------------
    # Collects user input from the Add Task window, creates a new task, updates the Home tab and Calendar
    def handle_add_task(self, title_entry, desc_text, day_vars, day_time_entries, day_ampm_vars, window):
        title = title_entry.get().strip()
        description = desc_text.get("1.0", tk.END).strip()
        reminder_schedule = {}
        for day in day_vars:
            if day_vars[day].get():
                time_str = day_time_entries[day].get().strip()
                ampm = day_ampm_vars[day].get().strip()
                full_time = f"{time_str} {ampm}"
                reminder_schedule[day] = full_time

        if title:
            task = {"title": title, "description": description, "reminder_schedule": reminder_schedule}
            self.tasks.append(task)
            schedule_summary = ", ".join([f"{day[:3]}: {reminder_schedule[day]}" for day in reminder_schedule])
            iid = str(len(self.tasks) - 1)
            self.task_tree.insert("", tk.END, iid=iid, values=(title, schedule_summary))
            self.update_custom_calendar()
            window.destroy()
        else:
            print("Task title is required.")

    # ------------------------------ EDIT TASK WINDOW ------------------------------
    # Opens a window that allows editing of an existing task
    def open_edit_task_window(self, index):
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Task")
        edit_window.geometry("500x600")
        
        form_frame = ttk.Frame(edit_window, padding=10)
        form_frame.pack(expand=True, fill='both')

        task = self.tasks[index]

        # Task Title
        title_label = ttk.Label(form_frame, text="Task Title:")
        title_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        title_entry = ttk.Entry(form_frame, font=("Helvetica", 11))
        title_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        title_entry.insert(0, task["title"])

        # Task Description
        desc_label = ttk.Label(form_frame, text="Description:")
        desc_label.grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        desc_text = tk.Text(form_frame, height=4, font=("Helvetica", 11))
        desc_text.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        desc_text.insert(tk.END, task["description"])

        # Reminder Schedule Section Heading
        schedule_label = ttk.Label(form_frame, text="Reminder Schedule:")
        schedule_label.grid(row=2, column=0, padx=5, pady=(10,5), sticky='w')

        schedule_frame = ttk.Frame(form_frame)
        schedule_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_vars = {}
        day_time_entries = {}
        day_ampm_vars = {}

        for i, day in enumerate(days):
            var = tk.BooleanVar(value=(day in task["reminder_schedule"]))
            day_vars[day] = var
            chk = ttk.Checkbutton(schedule_frame, text=day, variable=var)
            chk.grid(row=i, column=0, padx=5, pady=2, sticky='w')

            time_entry = ttk.Entry(schedule_frame, width=10, font=("Helvetica", 11))
            time_entry.grid(row=i, column=1, padx=5, pady=2, sticky='w')
            if day in task["reminder_schedule"]:
                parts = task["reminder_schedule"][day].split()
                time_entry.insert(0, parts[0])
            else:
                time_entry.insert(0, "HH:MM")
            day_time_entries[day] = time_entry

            ampm_var = tk.StringVar(value=(task["reminder_schedule"][day].split()[1] if day in task["reminder_schedule"] and len(task["reminder_schedule"][day].split()) > 1 else "AM"))
            day_ampm_vars[day] = ampm_var
            ampm_combo = ttk.Combobox(schedule_frame, textvariable=ampm_var, values=["AM", "PM"], width=5, font=("Helvetica", 11))
            ampm_combo.grid(row=i, column=2, padx=5, pady=2, sticky='w')

        update_btn = ttk.Button(form_frame, text="Update Task",
                                command=lambda: self.handle_update_task(index, title_entry, desc_text, day_vars, day_time_entries, day_ampm_vars, edit_window))
        update_btn.grid(row=4, column=0, columnspan=2, padx=5, pady=20)

        form_frame.columnconfigure(1, weight=1)

    # ------------------------------ TASK HANDLING FUNCTION ------------------------------
    def handle_update_task(self, index, title_entry, desc_text, day_vars, day_time_entries, day_ampm_vars, window):
        title = title_entry.get().strip()
        description = desc_text.get("1.0", tk.END).strip()

        reminder_schedule = {}
        for day in day_vars:
            if day_vars[day].get():
                time_str = day_time_entries[day].get().strip()
                ampm = day_ampm_vars[day].get().strip()
                full_time = f"{time_str} {ampm}"
                reminder_schedule[day] = full_time

        if title:
            self.tasks[index] = {"title": title, "description": description, "reminder_schedule": reminder_schedule}
            schedule_summary = ", ".join([f"{day[:3]}: {reminder_schedule[day]}" for day in reminder_schedule])
            self.task_tree.item(str(index), values=(title, schedule_summary))
            self.update_custom_calendar()
            window.destroy()
        else:
            print("Task title is required.")

    # ------------------------------ CUSTOM CALENDAR TAB ------------------------------
    def create_calendar_ui(self):
        # Create a container frame
        self.custom_calendar_frame = ttk.Frame(self.calendar_frame)
        self.custom_calendar_frame.pack(expand=True, fill='both')

        # Header for month navigation
        header_frame = ttk.Frame(self.custom_calendar_frame)
        header_frame.pack(fill='x', padx=10, pady=5)

        prev_btn = ttk.Button(header_frame, text="<", command=self.prev_month)
        prev_btn.pack(side='left')

        self.month_year_label = ttk.Label(header_frame, text="", font=("Helvetica", 16))
        self.month_year_label.pack(side='left', expand=True)

        next_btn = ttk.Button(header_frame, text=">", command=self.next_month)
        next_btn.pack(side='right')

        # Frame for the calendar grid
        self.calendar_grid_frame = ttk.Frame(self.custom_calendar_frame)
        self.calendar_grid_frame.pack(expand=True, fill='both', padx=10, pady=5)

        # Draw the calendar for the current month
        self.update_custom_calendar()

    # Updates the custom calendar grid with the current month/year and tasks
    def update_custom_calendar(self):
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()

        self.month_year_label.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        days_header = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for col, day_name in enumerate(days_header):
            lbl = ttk.Label(self.calendar_grid_frame, text=day_name, borderwidth=1, relief="solid", anchor="center", font=("Helvetica", 12, "bold"))
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
            self.calendar_grid_frame.columnconfigure(col, weight=1)

        # Get the matrix of weeks for the current month
        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)

        # Create grid: one row per week
        for row_index, week in enumerate(month_days, start=1):
            for col_index, day in enumerate(week):
                cell_frame = ttk.Frame(self.calendar_grid_frame, borderwidth=1, relief="solid")
                cell_frame.grid(row=row_index, column=col_index, sticky="nsew", padx=1, pady=1)
                self.calendar_grid_frame.rowconfigure(row_index, weight=1)

                if day != 0:
                    # Date number label at the top of the cell
                    date_lbl = ttk.Label(cell_frame, text=str(day), anchor="n", font=("Helvetica", 10, "bold"))
                    date_lbl.pack(fill="x")
                    # Determine day-of-week for this date
                    current_date = date(self.current_year, self.current_month, day)
                    day_name = current_date.strftime("%A")
                    # Find tasks for this day by matching day_name
                    task_texts = []
                    for task in self.tasks:
                        if day_name in task["reminder_schedule"]:
                            task_texts.append(f"{task['title']} @ {task['reminder_schedule'][day_name]}")
                    if task_texts:
                        tasks_lbl = ttk.Label(cell_frame, text="\n".join(task_texts), anchor="w", wraplength=100, font=("Helvetica", 9))
                        tasks_lbl.pack(fill="both", expand=True)
        self.calendar_grid_frame.update_idletasks()

    # Navigate to the previous month
    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_custom_calendar()

    # Navigate to the next month.
    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_custom_calendar()

# ------------------------------ MAIN EXECUTION BLOCK ------------------------------
if __name__ == "__main__":
    app = ConsistifyApp()
    app.mainloop()
