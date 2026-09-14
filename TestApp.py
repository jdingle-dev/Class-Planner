import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


class CourseSchedulerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Course Scheduler Dashboard")
        self.root.geometry("850x600")

        # Database connection setup
        self.conn = sqlite3.connect("scheduler_gui.db")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        messagebox.showinfo("Curriculum Guides", "https://www.ncat.edu/provost/academic-affairs/curriculum-guides/")
        self.create_tables()

        # Build GUI layout
        self.setup_ui()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS courses (
                code TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                credits INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS prerequisites (
                course_code TEXT NOT NULL,
                prereq_code TEXT NOT NULL,
                PRIMARY KEY (course_code, prereq_code)
            );

            CREATE TABLE IF NOT EXISTS course_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT NOT NULL,
                days TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS student_progress (
                course_code TEXT PRIMARY KEY,
                status TEXT CHECK(status IN ('COMPLETED', 'CURRENT'))
            );
        """)
        self.conn.commit()

    def setup_ui(self):
        # Configure Notebook (Tabs container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Course Catalog Input
        self.tab_courses = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_courses, text=" 1. Add Courses ")
        self.build_courses_tab()

        # Tab 2: Prerequisites Input
        self.tab_prereqs = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_prereqs, text=" 2. Set Prerequisites ")
        self.build_prereqs_tab()

        # Tab 3: Student Progress
        self.tab_progress = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_progress, text=" 3. Student Progress ")
        self.build_progress_tab()

        # Tab 4: Schedule Recommendations
        self.tab_results = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_results, text=" 4. Recommended Schedule ")
        self.build_results_tab()

        # Tabe 5: Delete Classes
        self.tab_delete = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_delete, text=" 5. Delete Schedule ")
        self.build_delete_tab()

    # ==========================================
    # TAB 1: ADD COURSES & SCHEDULES
    # ==========================================
    def build_courses_tab(self):
        frame = ttk.LabelFrame(self.tab_courses, text="Course Details", padding=15)
        frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame, text="Course Code (e.g., CS101):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_code = ttk.Entry(frame, width=20)
        self.entry_code.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Course Title:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_title = ttk.Entry(frame, width=30)
        self.entry_title.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Credits:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_credits = ttk.Entry(frame, width=10)
        self.entry_credits.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Days (e.g., MWF, TR):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_days = ttk.Entry(frame, width=10)
        self.entry_days.grid(row=3, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Start Time (24h HH:MM):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.entry_start = ttk.Entry(frame, width=10)
        self.entry_start.grid(row=4, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="End Time (24h HH:MM):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.entry_end = ttk.Entry(frame, width=10)
        self.entry_end.grid(row=5, column=1, sticky=tk.W, pady=5)

        btn_save = ttk.Button(frame, text="Add Course", command=self.save_course)
        btn_save.grid(row=6, column=0, columnspan=2, pady=15)

    def save_course(self):
        code = self.entry_code.get().strip().upper()
        title = self.entry_title.get().strip()
        credits = self.entry_credits.get().strip()
        days = self.entry_days.get().strip().upper()
        start = self.entry_start.get().strip()
        end = self.entry_end.get().strip()

        if not all([code, title, credits, days, start, end]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            credits_val = int(credits)
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO courses VALUES (?, ?, ?)", (code, title, credits_val))
            cursor.execute("INSERT INTO course_schedules (course_code, days, start_time, end_time) VALUES (?, ?, ?, ?)",
                           (code, days, start, end))
            self.conn.commit()
            messagebox.showinfo("Success", f"Course {code} added successfully!")

            # Clear inputs
            for entry in [self.entry_code, self.entry_title, self.entry_credits, 
                          self.entry_days, self.entry_start, self.entry_end]:
                entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Credits must be an integer.")

    # ==========================================
    # TAB 2: PREREQUISITES
    # ==========================================
    def build_prereqs_tab(self):
        frame = ttk.LabelFrame(self.tab_prereqs, text="Link Prerequisites", padding=15)
        frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame, text="Target Course Code (e.g., CS102):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_target_course = ttk.Entry(frame, width=20)
        self.entry_target_course.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Prerequisite Course (e.g., CS101):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_prereq_course = ttk.Entry(frame, width=20)
        self.entry_prereq_course.grid(row=1, column=1, pady=5)

        btn_link = ttk.Button(frame, text="Link Prerequisite", command=self.save_prereq)
        btn_link.grid(row=2, column=0, columnspan=2, pady=15)

    def save_prereq(self):
        course = self.entry_target_course.get().strip().upper()
        prereq = self.entry_prereq_course.get().strip().upper()

        if not course or not prereq:
            messagebox.showwarning("Input Error", "Both course fields are required.")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO prerequisites VALUES (?, ?)", (course, prereq))
        self.conn.commit()
        messagebox.showinfo("Success", f"Prerequisite {prereq} linked to {course}!")
        self.entry_target_course.delete(0, tk.END)
        self.entry_prereq_course.delete(0, tk.END)

    # ==========================================
    # TAB 3: STUDENT PROGRESS
    # ==========================================
    def build_progress_tab(self):
        frame = ttk.LabelFrame(self.tab_progress, text="Update Progress", padding=15)
        frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame, text="Course Code:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_prog_course = ttk.Entry(frame, width=20)
        self.entry_prog_course.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Status:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.combo_status = ttk.Combobox(frame, values=["COMPLETED", "CURRENT"], state="readonly")
        self.combo_status.grid(row=1, column=1, pady=5)
        self.combo_status.current(0)

        btn_save_prog = ttk.Button(frame, text="Update Progress", command=self.save_progress)
        btn_save_prog.grid(row=2, column=0, columnspan=2, pady=15)

    def save_progress(self):
        course = self.entry_prog_course.get().strip().upper()
        status = self.combo_status.get()

        if not course:
            messagebox.showwarning("Input Error", "Course code is required.")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO student_progress VALUES (?, ?)", (course, status))
        self.conn.commit()
        messagebox.showinfo("Success", f"Saved {course} as {status}!")
        self.entry_prog_course.delete(0, tk.END)

    # ==========================================
    # TAB 4: SCHEDULE RECOMMENDATIONS & TABLE
    # ==========================================
    def build_results_tab(self):
        btn_calculate = ttk.Button(self.tab_results, text="🔄 Generate Recommended Schedule", command=self.calculate_schedule)
        btn_calculate.pack(pady=10)

        # Setup Results Data Table (Treeview)
        columns = ("code", "title", "credits", "days", "time_slot", "conflicts")
        self.tree = ttk.Treeview(self.tab_results, columns=columns, show="headings", height=15)

        self.tree.heading("code", text="Code")
        self.tree.heading("title", text="Title")
        self.tree.heading("credits", text="Credits")
        self.tree.heading("days", text="Days")
        self.tree.heading("time_slot", text="Time Slot")
        self.tree.heading("conflicts", text="Conflicts With")

        self.tree.column("code", width=80)
        self.tree.column("title", width=200)
        self.tree.column("credits", width=60, anchor="center")
        self.tree.column("days", width=60, anchor="center")
        self.tree.column("time_slot", width=140, anchor="center")
        self.tree.column("conflicts", width=180)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def calculate_schedule(self):
        # Clear existing table data
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.conn.cursor()
        query = """
        WITH 
        passed_courses AS (
            SELECT course_code FROM student_progress
        ),
        courses_with_missing_prereqs AS (
            SELECT DISTINCT p.course_code 
            FROM prerequisites p
            WHERE p.prereq_code NOT IN (SELECT course_code FROM passed_courses)
        ),
        eligible_courses AS (
            SELECT 
                c.code, 
                c.title, 
                c.credits, 
                s.days, 
                s.start_time, 
                s.end_time
            FROM courses c
            JOIN course_schedules s ON c.code = s.course_code
            WHERE c.code NOT IN (SELECT course_code FROM passed_courses)
              AND c.code NOT IN (SELECT course_code FROM courses_with_missing_prereqs)
        )
        SELECT 
            e1.code,
            e1.title,
            e1.credits,
            e1.days,
            e1.start_time || ' - ' || e1.end_time AS time_slot,
            COALESCE(GROUP_CONCAT(e2.code, ', '), 'None') AS conflicts_with
        FROM eligible_courses e1
        LEFT JOIN eligible_courses e2 
          ON e1.code != e2.code
          AND (
               (e1.days LIKE '%M%' AND e2.days LIKE '%M%') OR
               (e1.days LIKE '%T%' AND e2.days LIKE '%T%') OR
               (e1.days LIKE '%W%' AND e2.days LIKE '%W%') OR
               (e1.days LIKE '%R%' AND e2.days LIKE '%R%') OR
               (e1.days LIKE '%F%' AND e2.days LIKE '%F%')
          )
          AND (MAX(e1.start_time, e2.start_time) < MIN(e1.end_time, e2.end_time))
        GROUP BY e1.code
        ORDER BY e1.code;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            messagebox.showinfo("No Results", "No eligible courses found for next semester.")
            return

        for row in results:
            self.tree.insert("", tk.END, values=row)

    def build_delete_tab(self):
        frame = ttk.LabelFrame(self.tab_delete, text="Delete Course", padding=15)
        frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame, text="Course Code:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_del_code = ttk.Entry(frame, width=20)
        self.entry_del_code.grid(row=0, column=1, pady=5)

        btn_del = ttk.Button(frame, text="Delete Courses", command=self.delete_course)
        btn_del.grid(row=2, column=1, columnspan=2, pady=15)

        btn_del_all = ttk.Button(frame, text="Delete All Courses", command=self.delete_all)
        btn_del_all.grid(row=4, column=1, columnspan=2, pady=15)

    def delete_course(self):
        cursor = self.conn.cursor()
        code = self.entry_del_code.get().strip().upper()
        if not code:
            messagebox.showwarning("Input Error", "Course code is required.")
            return

        
        cursor.execute(f"DELETE FROM courses WHERE code = '{code}';")
        cursor.execute(f"DELETE FROM course_schedules WHERE course_code = '{code}';")
        cursor.execute(f"DELETE FROM prerequisites WHERE course_code = '{code}';")
        cursor.execute(f"DELETE FROM student_progress WHERE course_code = '{code}';")
        self.conn.commit()
                
    def delete_all(self):
            cursor = self.conn.cursor()
            
            cursor.execute(f"DELETE FROM courses")
            cursor.execute(f"DELETE FROM course_schedules")
            cursor.execute(f"DELETE FROM prerequisites")
            cursor.execute(f"DELETE FROM student_progress")
            self.conn.commit()
                    



if __name__ == "__main__":
    root = tk.Tk()
    app = CourseSchedulerApp(root)
    root.mainloop()