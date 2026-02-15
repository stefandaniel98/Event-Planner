import json
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar, DateEntry
from database import Database
from models import EventManager
from notifications import NotificationScheduler
from themes import apply_theme
from reports import export_csv, export_json, import_csv, import_json


APP_DIR = Path(__file__).parent
CONFIG_PATH = APP_DIR / "config.json"

DEFAULT_CONFIG = {
    "theme": "Light",
}

class EventPlannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Event Planner")
        self.geometry("980x600")
        self.minsize(900, 560)

        self.db = Database()
        self.manager = EventManager(self.db)
        self.config_data = self._load_config()

        apply_theme(self, self.config_data.get("theme", "Light"))
        
        self._build_menu()
        self._build_layout()
        self._load_calendar_marks()
        self._bind_events()
        self._start_future_events_tick()

        self.notifier = NotificationScheduler(self.db)
        self.notifier.schedule_all()

        #--------------------Config-------------------------
      
    def _load_config(self):
        '''Loads the previously saved theme; if it doesn't exist, creates it with default values.'''
        if not CONFIG_PATH.exists():
            CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
            return DEFAULT_CONFIG.copy()
        
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return DEFAULT_CONFIG.copy()
        
    def _save_config(self):
        CONFIG_PATH.write_text(json.dumps(self.config_data, indent=2), encoding="utf-8")

# -----------------------------------------UI------------------------------------------------
    def _build_menu(self):
        '''Builds the application's top menu bar.'''
        menubar = tk.Menu(self)

        file_m = tk.Menu(menubar, tearoff=0)

        file_m.add_command(label="Import CSV", command=self._import_csv)
        file_m.add_command(label="Import JSON", command=self._import_json)
        file_m.add_separator()
        file_m.add_command(label="Export CSV", command=self._export_csv)
        file_m.add_command(label="Export JSON", command=self._export_json)
        file_m.add_separator()
        file_m.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_m)

        view_m = tk.Menu(menubar, tearoff=0)
        view_m.add_command(label="Toggle Light/Dark Mode", command=self._toggle_theme)
        menubar.add_cascade(label="View", menu=view_m)


        help_m = tk.Menu(menubar, tearoff=0)
        help_m.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_m)

        self.config(menu=menubar)

    def _build_layout(self):
        '''Builds the graphical user interface structure.'''
      
        root = ttk.Frame(self)
        root.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        
        root.columnconfigure(0, weight=3)   # 75% for calendar + tabel
        root.columnconfigure(1, weight=1)   # 25% for dashboard
        root.rowconfigure(0, weight=1)

        # Left side (calendar + butoane + tabel)
        left = ttk.Frame(root)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        left.rowconfigure(0, weight=3)   # calendar
        left.rowconfigure(1, weight=0)   # buttons
        left.rowconfigure(2, weight=5)   # table
        left.columnconfigure(0, weight=1)

        # Right side (dashboard)
        right = ttk.Frame(root)
        right.grid(row=0, column=1, sticky="nsew")

        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        # -------------------------
        #      RIGHT DASHBOARD 
        # -------------------------
        self.future_frame = ttk.Frame(right)
        self.future_frame.grid(row=0, column=0, sticky="nsew", padx=4, pady=8)

        # row0 = header, row1 = card container
        self.future_frame.rowconfigure(1, weight=1)
        self.future_frame.columnconfigure(0, weight=1)

        # Header
        header = tk.Frame(self.future_frame, bg="#E5E7EB", height=32)
        header.grid(row=0, column=0, sticky="ew")

        label = tk.Label(
            header,
            text="Upcoming Events",
            bg="#E5E7EB",
            fg="black",
            font=("Segoe UI", 10, "bold")
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

        # Card container
        self.future_container = ttk.Frame(self.future_frame)
        self.future_container.grid(row=1, column=0, sticky="nsew")

        # -------------------------
        #     Calendar area - left
        # -------------------------
        cal_frame = ttk.Frame(left)
        cal_frame.grid(row=0, column=0, sticky="nsew")

        cal_frame.rowconfigure(0, weight=1)
        cal_frame.columnconfigure(0, weight=1)

        self.cal = Calendar(cal_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.cal.grid(row=0, column=0, sticky="nsew")


        # -------------------------
        #        Buttons
        # -------------------------
        btns = ttk.Frame(left)
        btns.grid(row=1, column=0, sticky="ew", pady=10)

        btns.columnconfigure(0, weight=0)
        btns.columnconfigure(1, weight=0)
        btns.columnconfigure(2, weight=0)
        btns.columnconfigure(3, weight=0)

        ttk.Button(btns, text="📍 Today", command=self._go_today).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="➕ Add", command=self._add_dialog).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="✏️ Edit", command=self._edit_selected).grid(row=0, column=2, padx=4)
        ttk.Button(btns, text="🗑️ Delete", command=self._delete_selected).grid(row=0, column=3, padx=4)
        


        # -------------------------
        #          Table
        # -------------------------
        columns = ("id", "title", "time", "priority", "description")
        self.tree = ttk.Treeview(left, columns=columns, show="headings")

        #Table Headers
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("time", text="Time")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("description", text="Description")

        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("title", width=180)
        self.tree.column("time", width=80, anchor=tk.CENTER)
        self.tree.column("priority", width=80, anchor=tk.CENTER)
        self.tree.column("description", width=350)

        self.tree.grid(row=2, column=0, sticky="nsew", pady=(10, 0))



    def _bind_events(self):
        ''' Binds UI events to their respective functions.
            In this case, selecting a date in the calendar triggers
            an update of the event list for that specific day. '''
        self.cal.bind("<<CalendarSelected>>", lambda e: self._refresh_day())


    def _load_calendar_marks(self):
        ''' Highlights days with events in the calendar.
            Clears old marks, fetches dates from the database, and adds 
            a visual indicator for each day that has registered activities. '''
        self.cal.calevent_remove('all')
        for d in self.db.days_with_events():
            try:
                y, m, day = map(int, d.split('-'))
                self.cal.calevent_create(datetime(y,m,day), 'event', 'has_event')
            except Exception:
                pass
        self.cal.tag_config('has_event', background='#2563eb', foreground='white')


    # ---------------- Actions ----------------
    def _current_date(self):
        return self.cal.get_date()
    
    def _go_today(self):
        ''' Selects today's date in the calendar and refreshes the 
            event list for the current day. '''
        from datetime import date
        self.cal.selection_set(date.today())
        self._refresh_day()


    def _get_future_events(self):
        ''' Returns future events, sorted chronologically by date and time. '''    
        now = datetime.now()
        events = self.db.list_all()
        future = []


        for ev in events:
            try:
                dt = datetime.strptime(f"{ev['date']} {ev['time']}", "%Y-%m-%d %H:%M")
                if dt > now:
                    future.append((dt, ev))

            except:
                pass

        future.sort(key=lambda x: x[0])
        return [ev for dt, ev in future]
    
    def _refresh_future_events(self):
        ''' Reloads the dashboard with upcoming events:
            clears old cards, fetches future events, and displays 
            a colored card for each, including title, date/time, and countdown. '''
        for widget in self.future_container.winfo_children():
            widget.destroy()


        events = self._get_future_events()
        if not events:
            ttk.Label(self.future_container, text="No upcoming events").pack(anchor="w", padx=6, pady=4)
            return
    
        for ev in events:
            card = tk.Canvas(self.future_container, height=95, width=300,  highlightthickness=0, bg=self.cget("background"))

            card.pack( padx=6, pady=6, anchor="nw")

            colors = {
                "Low":  ("#15803D", "#DCFCE7"),
                "Medium": ("#D97706", "#FEF3C7"),
                "High":  ("#DC2626", "#FEE2E2")
            }

            outline_color, fill_color = colors.get(ev.get("priority"), ("#6b7280", "#e5e7eb"))
            card.create_rectangle(5,5,295,90, fill=fill_color, outline=outline_color, width=2)
            card.create_text(20,20, text=ev.get("title", ""), font=("Segoe UI", 10, "bold"), anchor="w")
            card.create_text(20,45, text=f"📅 {ev['date']}   🕒 {ev['time']}", anchor="w" )
            left = EventManager(self.db).countdown_for(ev)
            card.create_text(20,70, text=f"⏳ {left}", anchor='w' )


    def _refresh_day(self):
        ''' Updates events for the selected date:
            clears the table, loads the day's events, refreshes 
            calendar marks, and updates the upcoming events dashboard. '''
        for i in self.tree.get_children():
            self.tree.delete(i)
        date_str = self._current_date()
        events = self.manager.events_on(date_str)
        for ev in events:
            self.tree.insert(
                '',
                tk.END,
                values=(
                    ev['id'],
                    ev['title'],
                    ev['time'],
                    ev['priority'],
                    ev['description'] 
                )
            )
            
        self._load_calendar_marks()
        self._refresh_future_events()

    def _get_selected_event_id(self):
        ''' Returns the ID of the selected event from the table.
            If no row is selected, returns None. '''
        sel = self.tree.selection()
        if not sel:
            return None
        return int(self.tree.item(sel[0], 'values')[0])


    def _start_future_events_tick(self):
        ''' Starts the automatic dashboard refresh every minute. '''
        self._refresh_future_events()
        self.after(60_000, self._start_future_events_tick)

    def _add_dialog(self):
        ''' Opens the dialog window to add a new event. '''
        EventDialog(self, title="Adauga eveniment", on_save=self._add_event).show()


    def _add_event(self, data: dict):
        ''' Saves the new event, schedules notifications, and updates the UI. '''
        event_id = self.manager.add(**data)
        ev = self.db.get_event(event_id)
        self.notifier.schedule_event(ev)
        self._refresh_day()
        self._refresh_future_events()


    def _edit_selected(self):
        ''' Opens the edit dialog for the event currently selected in the table. '''
        event_id = self._get_selected_event_id()
        if not event_id:
            messagebox.showinfo("Info", "Please select an event from the list.")
            return
        ev = self.db.get_event(event_id)
        EventDialog(self,title="Edit Event", initial=ev, on_save=lambda d: self._update_event(event_id, d)).show()

    def _update_event(self, event_id: int, data: dict ):
        ''' Updates the event in the database, reschedules 
            notifications, and refreshes the interface. '''
        self.manager.update(event_id, **data)
        ev = self.db.get_event(event_id)
        self.notifier.schedule_event(ev)
        self._refresh_day()
        self._refresh_future_events()

    def _delete_selected(self):
        ''' Deletes the selected event from the table. '''
        event_id = self._get_selected_event_id()
        if not event_id:
            return
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected event?"):
            self.manager.delete(event_id)
            self._refresh_day()
            self._refresh_future_events()

    # ------------- Settings & Export/Import -------------

    def _toggle_theme(self):
        ''' Toggles between Light/Dark theme and saves the new preference. '''
        self.config_data["theme"] = "Dark" if self.config_data.get("theme") == "Light" else "Light"
        self._save_config()
        apply_theme(self, self.config_data["theme"])

    def _export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if path:
            export_csv(self.db, path)
            messagebox.showinfo("Export", "CSV Export completed succesfully.")

    def _export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if path:
            export_json(self.db, path)
            messagebox.showinfo("Export", "JSON Export completed succesfully.")
    
    def _import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if path:
            import_csv(self.db, path)
            self._refresh_day()
            messagebox.showinfo("Import", "CSV Import completed successfully.")  

    def _import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files","*.json")])
        if path:
            import_json(self.db, path)
            self._refresh_day()
            messagebox.showinfo("Import", "JSON Import completed successfully.")

    def on_close(self):
        ''' Stops notifications, closes the database connection, and exits the application. '''
        try:
            self.notifier.stop()
        finally:
            self.db.close()
            self.destroy()


    def _show_about(self):
        """ Displays the 'About' window with application information. """
        about = tk.Toplevel(self)
        about.title("Despre")
        about.resizable(False, False)
        about.transient(self)
        about.grab_set()

        frame = ttk.Frame(about, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Event Planner", font=("Segoe UI", 16, "bold")).pack(anchor="center", pady=(0,10))
        ttk.Label(frame, text="Version 1.0.0", font=("Segoe UI", 10, "italic")).pack(anchor="center")
        ttk.Separator(frame).pack(fill="x", pady=10)


        info = (
            "Creator: Mainea Ștefan Daniel\n"
            "Technologies: Python, Tkinter, SQLite\n"
            "Release Date: 2025\n\n"
            "Event Planner is a management application "
            "featuring:\n"
            " • Interactive Calendar\n"
            " • Add / Edit / Delete events\n"
            " • Color-coded priorities\n"
            " • Live countdown for each event\n"
            " • Automated notifications\n"
            " • CSV & JSON Export / Import\n"
            " • Light / Dark Theme support\n\n"
            "The purpose of this app is to provide a fast, clear, and "
            "intuitive way to organize personal events."
        )

        msg = tk.Message(
            frame,
            text=info,
            justify="left",
            width=380,
            font=("Segoe UI", 10)
        )   

        msg.pack(anchor="w", fill="both", expand=True)
        ttk.Separator(frame).pack(fill="x", pady=15)
        ttk.Button(frame, text="OK", command=about.destroy).pack(anchor="center")


        
class EventDialog:
    def __init__(self, master, title: str, on_save, initial: dict | None = None):
        ''' Initializes the dialog window and form fields. '''
        self.master = master
        self.initial = initial or {}
        self.on_save = on_save
        self.top = tk.Toplevel(master)
        self.top.title(title)
        self.top.transient(master)
        self.top.grab_set()


        frm = ttk.Frame(self.top)
        frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Title Field
        ttk.Label(frm, text="Title").grid(row=0, column=0, sticky='e', padx=6, pady=4)
        self.title_var = tk.StringVar(value=self.initial.get('title',''))
        ttk.Entry(frm, textvariable=self.title_var, width=40).grid(row=0, column=1, sticky='w')

        # Description Field
        ttk.Label(frm, text="Description").grid(row=1, column=0, sticky='ne', padx=6, pady=4)
        self.desc_txt = tk.Text(frm, height=5, width=40, wrap=tk.WORD)
        self.desc_txt.grid(row=1, column=1, sticky='w')
        self.desc_txt.insert('1.0', self.initial.get('description',''))

        # Data Field
        ttk.Label(frm, text="Date").grid(row=2, column=0, sticky='e', padx=6, pady=4)
        self.date_entry = DateEntry(frm, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=2, column=1, sticky='w')
        if self.initial.get('date'):

            y,m,d = map(int, self.initial['date'].split('-'))
            self.date_entry.set_date(datetime(y,m,d))

        # Time Field
        ttk.Label(frm, text="Time").grid(row=3, column=0, sticky='e', padx=6, pady=4)
        times = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0,15,30,45)]
        self.time_var = tk.StringVar(value=self.initial.get('time','09:00'))
        ttk.Combobox(frm, textvariable=self.time_var, values=times, width=7, state='readonly').grid(row=3, column=1, sticky='w')

        # Priority Field
        ttk.Label(frm, text="Priority").grid(row=4, column=0, sticky='e', padx=6, pady=4)
        self.pri_var = tk.StringVar(value=self.initial.get('priority','Medium'))
        ttk.Combobox(frm, textvariable=self.pri_var, values=['Low','Medium','High'], width=10, state='readonly').grid(row=4, column=1, sticky='w')

        # Dialog Buttons
        buttons = ttk.Frame(frm)
        buttons.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(buttons, text="Save", command=self._save).pack(side=tk.LEFT, padx=6)
        ttk.Button(buttons, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT, padx=6)


    def _save(self):
        ''' Saves the input data and closes the dialog. '''
        data = {
            'title': self.title_var.get().strip(),
            'description': self.desc_txt.get('1.0', tk.END).strip(),
            'date': self.date_entry.get_date().strftime('%Y-%m-%d'),
            'time': self.time_var.get(),
            'priority': self.pri_var.get()
        }
        if not data['title']:
            messagebox.showerror("Eroare", "Title is required.")
            return
        self.on_save(data)
        self.top.destroy()


    def show(self):
        ''' Opens the dialog in modal mode. '''
        self.top.wait_window()

if __name__ == '__main__':
    app = EventPlannerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()