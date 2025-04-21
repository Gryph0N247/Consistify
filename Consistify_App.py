# ------------------------------ MODULE IMPORTS ------------------------------
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk         # Modern themed window styling
from datetime import datetime, date, timedelta  # Date/time handling
import calendar                        # Month calculations
import threading, time
import winsound                        # System sounds on Windows

# ------------------------------ MAIN APPLICATION CLASS ------------------------------
class ConsistifyApp(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.title("Consistify: Smart Reminder & Task Manager")
        self.geometry("900x800")
        
        # Tasks: each has title, description, reminder_schedule (day→"HH:MM AM/PM"),
        # status ("pending"/"reminding"/"completed"), and next_reminder (datetime)
        self.tasks = []

        # Selected notification sound
        self.sound_var = tk.StringVar(value="SystemExclamation")

        # Calendar state
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month

        # Create tabbed interface
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        self.home_frame = ttk.Frame(notebook)
        self.calendar_frame = ttk.Frame(notebook)
        notebook.add(self.home_frame, text='Home')
        notebook.add(self.calendar_frame, text='Calendar')

        # Build UI
        self.create_home_ui()
        self.create_calendar_ui()

        # Start background reminder thread
        threading.Thread(target=self.reminder_loop, daemon=True).start()

    # ------------------------------ HOME TAB UI ------------------------------
    def create_home_ui(self):
        # Notification Sound Selector
        ttk.Label(self.home_frame, text="Notification Sound:", font=("Helvetica",12))\
            .grid(row=0, column=0, padx=10, pady=5, sticky='w')
        ttk.Combobox(
            self.home_frame, textvariable=self.sound_var,
            values=["SystemAsterisk","SystemExclamation","SystemHand","SystemQuestion"],
            state="readonly", width=20
        ).grid(row=1, column=0, padx=10, pady=(0,10), sticky='w')

        # Task List Label
        ttk.Label(self.home_frame, text="Your Tasks:", font=("Helvetica",14))\
            .grid(row=2, column=0, padx=10, pady=5, sticky='w')

        # Treeview for Tasks
        style = ttk.Style()
        style.configure("Treeview", rowheight=60, font=("Helvetica",12))
        self.task_tree = ttk.Treeview(
            self.home_frame, columns=("title","schedule"), show='headings'
        )
        self.task_tree.heading("title", text="Task Title", anchor='center')
        self.task_tree.heading("schedule", text="Schedule", anchor='center')
        self.task_tree.column("title", anchor="center", width=400)
        self.task_tree.column("schedule", anchor="center", width=400)
        self.task_tree.grid(row=3, column=0, padx=10, pady=5, sticky='nsew')
        self.task_tree.bind("<Double-1>", self.on_double_click)

        # Add New Task Button
        ttk.Style().configure("Big.TButton", font=("Helvetica",16), padding=10)
        ttk.Button(
            self.home_frame, text="Add New Task", style="Big.TButton",
            command=self.open_add_task_window
        ).grid(row=4, column=0, padx=10, pady=10, sticky='ew')

        self.home_frame.rowconfigure(3, weight=1)
        self.home_frame.columnconfigure(0, weight=1)

    # ------------------------------ DOUBLE-CLICK HANDLER ------------------------------
    def on_double_click(self, event):
        sel = self.task_tree.selection()
        if sel:
            self.open_edit_task_window(int(sel[0]))

    # ------------------------------ ADD TASK WINDOW ------------------------------
    def open_add_task_window(self):
        win = tk.Toplevel(self)
        win.title("Add New Task")
        win.geometry("500x600")
        frm = ttk.Frame(win, padding=10); frm.pack(expand=True, fill='both')

        # Title
        ttk.Label(frm, text="Task Title:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        title_e = ttk.Entry(frm, font=("Helvetica",11)); title_e.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Description
        ttk.Label(frm, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        desc_t = tk.Text(frm, height=4, font=("Helvetica",11)); desc_t.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Reminder Schedule
        ttk.Label(frm, text="Reminder Schedule:").grid(row=2, column=0, padx=5, pady=(10,5), sticky='w')
        sched = ttk.Frame(frm); sched.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_vars, t_entries, ap_vars = {}, {}, {}
        for i, d in enumerate(days):
            day_vars[d] = tk.BooleanVar()
            ttk.Checkbutton(sched, text=d, variable=day_vars[d])\
                .grid(row=i, column=0, padx=5, pady=2, sticky='w')
            e = ttk.Entry(sched, width=10, font=("Helvetica",11)); e.grid(row=i, column=1, padx=5, pady=2); e.insert(0,"HH:MM"); t_entries[d]=e
            ap_vars[d] = tk.StringVar(value="AM")
            ttk.Combobox(sched, textvariable=ap_vars[d],
                         values=["AM","PM"], width=5, font=("Helvetica",11))\
                .grid(row=i, column=2, padx=5, pady=2, sticky='w')

        ttk.Button(
            frm, text="Submit Task",
            command=lambda: self.handle_add_task(title_e, desc_t, day_vars, t_entries, ap_vars, win)
        ).grid(row=4, column=0, columnspan=2, padx=5, pady=20)
        frm.columnconfigure(1, weight=1)

    # ------------------------------ HANDLE ADD TASK ------------------------------
    def handle_add_task(self, title_e, desc_t, day_vars, t_entries, ap_vars, win):
        title = title_e.get().strip()
        desc = desc_t.get("1.0", tk.END).strip()
        schedule = {}
        for d, var in day_vars.items():
            if var.get():
                t = t_entries[d].get().strip()
                ap = ap_vars[d].get().strip()
                schedule[d] = f"{t} {ap}"

        if not title:
            return

        idx = len(self.tasks)
        next_r = self.compute_next_reminder(schedule)
        task = {
            "title": title,
            "description": desc,
            "reminder_schedule": schedule,
            "status": "pending",
            "next_reminder": next_r
        }
        self.tasks.append(task)
        summary = ", ".join(f"{d[:3]}: {schedule[d]}" for d in schedule)
        self.task_tree.insert("", tk.END, iid=str(idx), values=(title, summary))
        win.destroy()

    # ------------------------------ EDIT TASK WINDOW ------------------------------
    def open_edit_task_window(self, idx):
        task = self.tasks[idx]
        win = tk.Toplevel(self)
        win.title("Edit Task"); win.geometry("500x600")
        frm = ttk.Frame(win, padding=10); frm.pack(expand=True, fill='both')

        ttk.Label(frm, text="Task Title:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        te = ttk.Entry(frm, font=("Helvetica",11)); te.grid(row=0, column=1, sticky='ew', padx=5); te.insert(0, task["title"])
        ttk.Label(frm, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        dt = tk.Text(frm, height=4, font=("Helvetica",11)); dt.grid(row=1, column=1, sticky='ew', padx=5); dt.insert(tk.END, task["description"])

        ttk.Label(frm, text="Reminder Schedule:").grid(row=2, column=0, padx=5, pady=(10,5), sticky='w')
        sched = ttk.Frame(frm); sched.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_vars, t_entries, ap_vars = {}, {}, {}
        for i, d in enumerate(days):
            val = d in task["reminder_schedule"]
            day_vars[d] = tk.BooleanVar(value=val)
            ttk.Checkbutton(sched, text=d, variable=day_vars[d])\
                .grid(row=i, column=0, padx=5, pady=2, sticky='w')
            e = ttk.Entry(sched, width=10, font=("Helvetica",11)); e.grid(row=i, column=1, padx=5, pady=2)
            if val:
                p = task["reminder_schedule"][d].split()
                e.insert(0, p[0])
            else:
                e.insert(0, "HH:MM")
            t_entries[d] = e
            ap_vars[d] = tk.StringVar(value=(task["reminder_schedule"][d].split()[1] if val else "AM"))
            ttk.Combobox(sched, textvariable=ap_vars[d],
                         values=["AM","PM"], width=5, font=("Helvetica",11))\
                .grid(row=i, column=2, padx=5, pady=2, sticky='w')

        ttk.Button(
            frm, text="Update Task",
            command=lambda: self.handle_update_task(idx, te, dt, day_vars, t_entries, ap_vars, win)
        ).grid(row=4, column=0, columnspan=2, padx=5, pady=20)
        frm.columnconfigure(1, weight=1)

    # ------------------------------ HANDLE UPDATE TASK ------------------------------
    def handle_update_task(self, idx, te, dt, day_vars, t_entries, ap_vars, win):
        title = te.get().strip()
        desc = dt.get("1.0", tk.END).strip()
        schedule = {}
        for d, var in day_vars.items():
            if var.get():
                t = t_entries[d].get().strip()
                ap = ap_vars[d].get().strip()
                schedule[d] = f"{t} {ap}"

        if not title:
            return

        next_r = self.compute_next_reminder(schedule)
        self.tasks[idx] = {
            "title": title,
            "description": desc,
            "reminder_schedule": schedule,
            "status": "pending",
            "next_reminder": next_r
        }
        summary = ", ".join(f"{d[:3]}: {schedule[d]}" for d in schedule)
        self.task_tree.item(str(idx), values=(title, summary))
        win.destroy()

    # ------------------------------ COMPUTE NEXT REMINDER ------------------------------
    def compute_next_reminder(self, schedule):
        now = datetime.now()
        candidates = []
        for day, timestr in schedule.items():
            try:
                tm = datetime.strptime(timestr, "%I:%M %p").time()
            except ValueError:
                continue
            wd = list(calendar.day_name).index(day)
            days_ahead = (wd - now.weekday() + 7) % 7
            dtc = datetime.combine(now.date() + timedelta(days=days_ahead), tm)
            if dtc <= now:
                dtc += timedelta(days=7)
            candidates.append(dtc)
        return min(candidates) if candidates else None

    # ------------------------------ REMINDER LOOP ------------------------------
    def reminder_loop(self):
        while True:
            now = datetime.now()
            for idx, task in enumerate(self.tasks):
                if task["status"] == "pending" and task["next_reminder"] and now >= task["next_reminder"]:
                    task["status"] = "reminding"
                    self.after(0, lambda idx=idx: self.show_reminder_popup(idx))
            time.sleep(30)

    # ------------------------------ REMINDER POPUP ------------------------------
    def show_reminder_popup(self, idx):
        task = self.tasks[idx]
        popup = tk.Toplevel(self)
        popup.title("Reminder")
        popup.geometry("300x150")
        ttk.Label(popup, text=f"Reminder: {task['title']}", font=("Helvetica",12,"bold")).pack(pady=10)
        ttk.Label(popup, text=task["description"], wraplength=280).pack(pady=5)
        btnf = ttk.Frame(popup); btnf.pack(pady=10)
        # Snooze and Complete both stop the looping sound
        ttk.Button(btnf, text="Snooze 5 min", command=lambda: self.snooze(idx, popup)).pack(side='left', padx=5)
        ttk.Button(btnf, text="Complete",    command=lambda: self.complete(idx, popup)).pack(side='left', padx=5)
        # Start looping the sound until stopped
        self.play_sound_loop()

    # ------------------------------ SNOOZE & COMPLETE ------------------------------
    def snooze(self, idx, popup):
        self.stop_sound()
        popup.destroy()
        self.tasks[idx]["next_reminder"] = datetime.now() + timedelta(minutes=5)
        self.tasks[idx]["status"] = "pending"

    def complete(self, idx, popup):
        self.stop_sound()
        popup.destroy()
        self.tasks[idx]["status"] = "completed"

    # ------------------------------ SOUND PLAYBACK ------------------------------
    def play_sound_loop(self):
        sound = self.sound_var.get()
        try:
            winsound.PlaySound(sound, winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
        except:
            self.bell()

    def stop_sound(self):
        winsound.PlaySound(None, winsound.SND_PURGE)

    # ------------------------------ CUSTOM CALENDAR TAB ------------------------------
    def create_calendar_ui(self):
        cf = ttk.Frame(self.calendar_frame); cf.pack(expand=True, fill='both')
        hdr = ttk.Frame(cf); hdr.pack(fill='x', padx=10, pady=5)
        ttk.Button(hdr, text="<", command=self.prev_month).pack(side='left')
        self.month_year_lbl = ttk.Label(hdr, font=("Helvetica",16)); self.month_year_lbl.pack(side='left', expand=True)
        ttk.Button(hdr, text=">", command=self.next_month).pack(side='right')
        self.grid_fr = ttk.Frame(cf); self.grid_fr.pack(expand=True, fill='both', padx=10, pady=5)
        self.update_custom_calendar()

    def update_custom_calendar(self):
        for w in self.grid_fr.winfo_children():
            w.destroy()
        self.month_year_lbl.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")
        days_h = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
        for c, d in enumerate(days_h):
            ttk.Label(self.grid_fr, text=d, anchor='center',
                      font=("Helvetica",12,"bold"), borderwidth=1, relief="solid")\
                .grid(row=0, column=c, sticky='nsew', padx=1, pady=1)
            self.grid_fr.columnconfigure(c, weight=1)

        events_by_day = {}
        for task in self.tasks:
            for day, ts in task["reminder_schedule"].items():
                events_by_day.setdefault(day, []).append(f"{task['title']} @ {ts}")

        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)
        for r, week in enumerate(month_days, start=1):
            self.grid_fr.rowconfigure(r, weight=1)
            for c, day_num in enumerate(week):
                cell = ttk.Frame(self.grid_fr, borderwidth=1, relief="solid")
                cell.grid(row=r, column=c, sticky='nsew', padx=1, pady=1)
                if day_num:
                    ttk.Label(cell, text=str(day_num), anchor='n',
                              font=("Helvetica",10,"bold")).pack(fill='x')
                    d = date(self.current_year, self.current_month, day_num)
                    dn = d.strftime("%A")
                    if dn in events_by_day:
                        ttk.Label(cell, text="\n".join(events_by_day[dn]),
                                  anchor='w', wraplength=100, font=("Helvetica",9))\
                            .pack(fill='both', expand=True)

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12; self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_custom_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1; self.current_year += 1
        else:
            self.current_month += 1
        self.update_custom_calendar()

# ------------------------------ MAIN EXECUTION BLOCK ------------------------------
if __name__ == "__main__":
    app = ConsistifyApp()
    app.mainloop()
