import csv
import sqlite3
from datetime import date


# Connect to SQLite database
conn = sqlite3.connect('schooldb.db')
c = conn.cursor()

def create_tables():
    # Define table creation queries here
    c.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            registration_date TEXT NOT NULL DEFAULT CURRENT_DATE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS Grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            grade INTEGER NOT NULL,
            date TEXT NOT NULL DEFAULT CURRENT_DATE,
            FOREIGN KEY (student_id) REFERENCES Students(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS Attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL DEFAULT CURRENT_DATE,
            present BOOLEAN NOT NULL,
            FOREIGN KEY (student_id) REFERENCES Students(id)
        )
    """)
    conn.commit()
    
create_tables()



def get_user_choice():
    print("\nSchool Management System")
    print("1. Add Student")
    print("2. View Students")
    print("3. Search Students")
    print("4. Update Student Information")
    print("5. Delete Student")
    print("6. Add Grade")
    print("7. View Grades")
    print("8. View Student Grades")
    print("9. Add Attendance")
    print("10. View Attendances")
    print("11. View Student Attendance")
    print("12. Export Data to CSV")
    print("13. Quit")

    while True:
        try:
            option = int(input('Choose an option: '))
            return option
        except ValueError:
            print("Invalid input. Please enter a number.")


def add_student():
    name = input('Enter student name: ')
    try:
        c.execute("INSERT INTO Students (name) VALUES (?)", (name,))
        conn.commit()
        print("Student added successfully!")
    except sqlite3.IntegrityError:
        print("Error: Student name already exists.")


def view_students():
    c.execute("SELECT * FROM Students")
    rows = c.fetchall()
    if not rows:
        print("No students found.")
    else:
        print("\nStudents:")
        for row in rows:
            print(row)
            
def search_students():
    search_term = input("Enter student name (or part of the name) to search: ")
    c.execute(f"SELECT * FROM Students WHERE name LIKE '%{search_term}%'")
    rows = c.fetchall()
    if not rows:
        print("No students found matching the search term.")
    else:
        print("\nSearch Results:")
        for row in rows:
            print(row)
            print(f"Student ID: {row[0]}")
            print(f"Student Name: {row[1]}")

def update_student():
    student_id = int(input("Enter student ID to update: "))
    new_name = input("Enter new student name (leave blank to keep old name): ")

    if new_name:
        c.execute(f"UPDATE Students SET name = ? WHERE id = {student_id}", (new_name,))
    else:
        c.execute(f"SELECT name FROM Students WHERE id = {student_id}")
        old_name = c.fetchone()[0]  # Get the current name

    conn.commit()
    if new_name:
        print(f"Student name updated from '{old_name}' to '{new_name}'.")
    else:
        print(f"Student name remains unchanged.")

def delete_student():
    student_id = int(input("Enter student ID to delete: "))

    # Check if student exists and has any grades/attendance records
    c.execute(f"SELECT * FROM Students WHERE id = {student_id}")
    student = c.fetchone()
    if not student:
        print("Error: Student not found.")
        return

    confirm = input(f"Are you sure you want to delete student '{student[1]}'? (yes/no): ").lower() == 'yes'
    if not confirm:
        print("Student deletion canceled.")
        return
    
    # Delete student's grades and attendance records
    c.execute(f"DELETE FROM Grades WHERE student_id = {student_id}")
    c.execute(f"DELETE FROM Attendance WHERE student_id = {student_id}")
    conn.commit()
    print(f"Student '{student[1]}' deleted successfully.")



def add_grade():
    student_id = int(input('Enter student id: '))
    # Ensure student exists before adding grade
    c.execute(f"SELECT * FROM Students WHERE id = {student_id}")
    if not c.fetchone():
        print(f"Error: Student with ID {student_id} not found.")
        return

    subject = input('Enter subject name: ')
    try:
        grade = int(input('Enter grade (must be a number): '))
        c.execute("INSERT INTO Grades (student_id, subject, grade) VALUES (?, ?, ?)", (student_id, subject, grade))
        conn.commit()
        print("Grade added successfully!")
    except ValueError:
        print("Error: Invalid grade. Please enter a number.")

def view_grades():
    c.execute("SELECT * FROM Grades")
    rows = c.fetchall()
    if not rows:
        print("No grades found.")
    else:
        print("\nGrades:")
        for row in rows:
            print(row)

def view_student_grades():
    student_id = int(input('Enter student id: '))
    c.execute(f"SELECT * FROM Grades WHERE student_id = {student_id}")
    rows = c.fetchall()
    if not rows:
        print("No grades found for this student.")
    else:
        print("\nStudent Grades:")
        for row in rows:
            print(row)


def add_attendance():
    student_id = int(input('Enter student id: '))
    # Ensure student exists before adding attendance
    c.execute(f"SELECT * FROM Students WHERE id = {student_id}")
    if not c.fetchone():
        print(f"Error: Student with ID {student_id} not found.")
        return

    present = input('Is the student present? (yes/no): ').lower() == 'yes'
    c.execute("INSERT INTO Attendance (student_id, present) VALUES (?, ?)", (student_id, present))
    conn.commit()
    print("Attendance added successfully!")


def view_attendances():
    c.execute("SELECT * FROM Attendance")
    rows = c.fetchall()
    if not rows:
        print("No attendances found.")
    else:
        print("\nAttendances:")
        for row in rows:
            print(row)

def view_student_attendance():
    student_id = int(input('Enter student id: '))
    c.execute(f"SELECT * FROM Attendance WHERE student_id = {student_id}")
    rows = c.fetchall()
    if not rows:
        print("No attendance records found for this student.")
    else:
        print("\nStudent Attendance:")
        for row in rows:
            print(row)


def export_to_csv():
    table_name = input("Enter the table name to export (Students, Grades, Attendance): ").lower()
    valid_tables = ["students", "grades", "attendance"]
    if table_name not in valid_tables:
        print("Invalid table name.")
        return

    try:
        # Construct the query to fetch data
        query = f"SELECT * FROM {table_name}"
        c.execute(query)
        rows = c.fetchall()

        if not rows:
            print(f"No data found in {table_name} table.")
            return

        # Generate a filename based on the table name and current date
        today = date.today().strftime("%Y-%m-%d")
        filename = f"{table_name}_{today}.csv"

        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write header row
            csv_writer.writerow([col[0] for col in c.description])  # Get column names
            # Write data rows
            csv_writer.writerows(rows)
        print(f"Data exported successfully to '{filename}'.")

    except sqlite3.Error as e:
        print("Error:", e)
        
        

def main():
    create_tables()  # Call this function to create tables if they don't exist
    while True:
        option = get_user_choice()
        if option == 1:
            add_student()
        elif option == 2:
            view_students()
        elif option == 3:
            search_students()
        elif option == 4:
            update_student()
        elif option == 5:
            delete_student()
        elif option == 6:
            add_grade()
        elif option == 7:
            view_grades()
        elif option == 8:
            view_student_grades()
        elif option == 9:
            add_attendance()
        elif option == 10:
            view_attendances()
        elif option == 11:
            view_student_attendance()
        elif option == 12:
            export_to_csv()
        elif option == 13:
            print("Exiting School Management System.")
            conn.close()  # Close the database connection
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()