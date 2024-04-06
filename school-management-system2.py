import csv
import sqlite3
from datetime import date


# Connect to SQLite database
conn = sqlite3.connect('schooldb.db')
c = conn.cursor()

def create_tables():
  """
  Creates necessary tables for student, grades, attendance, grades scale, and class management.
  """
  c.execute("""
    CREATE TABLE IF NOT EXISTS Students (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      registration_date TEXT NOT NULL DEFAULT CURRENT_DATE
    )
  """)
  c.execute("""
    CREATE TABLE IF NOT EXISTS Grades_Scale (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      grade_level INTEGER NOT NULL UNIQUE
    )
  """)
  c.execute("""
    CREATE TABLE IF NOT EXISTS Grades (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      subject TEXT NOT NULL,
      grade INTEGER NOT NULL,
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
  
  c.execute("""
    CREATE TABLE IF NOT EXISTS Classes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      class_name TEXT NOT NULL UNIQUE,
      grade_level INTEGER NOT NULL REFERENCES Grades_Scale(grade_level)
    )
  """)
  
  c.execute("""
    CREATE TABLE IF NOT EXISTS Student_Class (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL REFERENCES Students(id),
      class_id INTEGER NOT NULL REFERENCES Classes(id),
      FOREIGN KEY (student_id, class_id)
        REFERENCES Students(id, id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
        DEFERRABLE INITIALLY DEFERRED
        )
  """)
  conn.commit()

create_tables()

def get_user_choice():
  """
  Presents the user menu and retrieves their choice.
  """
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
  print("12. Class Management")
  print("   12.1. Add Class")
  print("   12.2. View Classes")
  print("   12.3. Assign Student to Class")
  print("   12.4. View Students in a Class")
  print("13. Export Data to CSV")
  print("14. Quit")

  while True:
    try:
      option = int(input('Choose an option: '))
      return option
    except ValueError:
      print("Invalid input. Please enter a number.")


def add_student():
  """
  Prompts for student details and optionally assigns them to a class.
  """
  name = input('Enter student name: ')
  class_name = input('Enter class name (optional): ')
  try:
    c.execute("INSERT INTO Students (name) VALUES (?)", (name,))
    conn.commit()
    print("Student added successfully!")
    if class_name:
      # Check if class exists
      c.execute("SELECT * FROM Classes WHERE class_name = ?", (class_name,))
      class_row = c.fetchone()
      if not class_row:
        print(f"Error: Class '{class_name}' not found.")
        return
      class_id = class_row[0]
      c.execute("INSERT INTO Student_Class (student_id, class_id) VALUES (?, ?)", (student_id, class_id))
      conn.commit()
      print(f"Student assigned to class '{class_name}'.")
  except sqlite3.IntegrityError:
    print("Error: Student name already exists.")


def view_students():
  """
  Retrieves and displays all student information, including their class (if assigned).
  """
  c.execute("SELECT s.id, s.name, c.class_name FROM Students s LEFT JOIN Student_Class sc ON s.id = sc.student_id LEFT JOIN Classes c ON sc.class_id = c.id")
  rows = c.fetchall()
  if not rows:
    print("No students found.")
  else:
    print("\nStudents:")
    for row in rows:
      class_name = row[2] if row[2] else "Unassigned"  # Handle students not assigned to a class
      print(f"Student ID: {row[0]}")
      print(f"Student Name: {row[1]}")
      print(f"Class: {class_name}")
      print("-" * 30)


def search_students():
  """
  Searches for students by name and displays their information.
  """
  search_term = input("Enter student name (or part of the name) to search: ")
  c.execute(f"SELECT s.id, s.name, c.class_name FROM Students s LEFT JOIN Student_Class sc ON s.id = sc.student_id LEFT JOIN Classes c ON sc.class_id = c.id WHERE s.name LIKE '%{search_term}%'")
  rows = c.fetchall()
  if not rows:
    print("No students found matching the search term.")
  else:
    print("\nSearch Results:")
    for row in rows:
      class_name = row[2] if row[2] else "Unassigned"
      print(f"Student ID: {row[0]}")
      print(f"Student Name: {row[1]}")
      print(f"Class: {class_name}")
      print("-" * 30)


def update_student():
  """
  Allows updating a student's name and optionally their class assignment.
  """
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

  # Update class assignment (optional)
  update_class = input("Update class assignment? (yes/no): ").lower() == 'yes'
  if update_class:
    new_class_name = input("Enter new class name (leave blank to keep current class): ")
    if new_class_name:
      # Check if new class exists
      c.execute("SELECT * FROM Classes WHERE class_name = ?", (new_class_name,))
      class_row = c.fetchone()
      if not class_row:
        print(f"Error: Class '{new_class_name}' not found.")
        return
      new_class_id = class_row[0]

      # Remove student from previous class (if assigned)
      c.execute("DELETE FROM Student_Class WHERE student_id = ?", (student_id,))

      # Assign student to the new class
      c.execute("INSERT INTO Student_Class (student_id, class_id) VALUES (?, ?)", (student_id, new_class_id))
      conn.commit()
      print(f"Student assigned to class '{new_class_name}'.")


def delete_student():
  """
  Deletes a student and their associated grades and attendance records.
  """
  student_id = int(input("Enter student ID to delete: "))

  # Check if student exists and has any grades/attendance records
  c.execute(f"SELECT * FROM Students WHERE id = {student_id}")
  student = c.fetchone()
  if not student:
    print("Error: Student not found.")
    return

  confirm = input(f"Are you sure you want to delete student '{student[1]}'? This will also remove their grades and attendance records. (yes/no): ").lower() == 'yes'
  if not confirm:
    print("Deletion cancelled.")
    return

  # Delete student, grades, and attendance records
  c.execute("DELETE FROM Attendance WHERE student_id = ?", (student_id,))
  c.execute("DELETE FROM Grades WHERE student_id = ?", (student_id,))
  c.execute("DELETE FROM Student_Class WHERE student_id = ?", (student_id,))
  c.execute("DELETE FROM Students WHERE id = ?", (student_id,))
  conn.commit()

  print("Student deleted successfully.")


def add_grade():
  """
  Prompts for student ID, subject, grade, and checks for valid grade level.
  """
  student_id = int(input('Enter student ID: '))
  # ... (existing code to check student existence)
  subject = input('Enter subject name: ')
  grade = int(input('Enter grade (must be a number): '))
  # Check if grade level exists in Grades_Scale table
  c.execute("SELECT grade_level FROM Student_Class sc JOIN Classes c ON sc.class_id = c.id WHERE sc.student_id = ?", (student_id,))
  grade_level_row = c.fetchone()
  if not grade_level_row:
    print("Error: Student not assigned to a class. Please assign a class first.")
    return
  grade_level = grade_level_row[0]
  # Ensure grade is within valid range for the student's grade level
  c.execute("SELECT * FROM Grades_Scale WHERE grade_level = ?", (grade_level,))
  if not c.fetchone():
    print(f"Error: Invalid grade level for student. Please enter a grade between 1 and {grade_level}.")
    return

  c.execute("INSERT INTO Grades (student_id, subject, grade) VALUES (?, ?, ?)", (student_id, subject, grade))
  conn.commit()
  print("Grade added successfully!")


def view_grades():
  """
  Displays all grades for all students.
  """
  c.execute("""
    SELECT s.name, su.subject, g.grade
    FROM Students s
    JOIN Grades g ON s.id = g.student_id
    JOIN Classes c ON g.student_id = c.student_id
    JOIN Student_Class sc ON c.id = sc.class_id
    JOIN Grades_Scale gs ON c.grade_level = gs.grade_level
    ORDER BY s.name, gs.grade_level, su.subject
  """)
  rows = c.fetchall()
  if not rows:
    print("No grades found.")
  else:
    print("\nAll Grades:")
    for row in rows:
      print(f"Student Name: {row[0]}")
      print(f"Subject: {row[1]}")
      print(f"Grade: {row[2]}")
      print("-" * 30)


def view_student_grades():
  """
  Displays all grades for a specific student.
  """
  student_id = int(input('Enter student ID: '))
  # ... (existing code to check student existence)
  c.execute("""
    SELECT su.subject, g.grade
    FROM Students s
    JOIN Grades g ON s.id = g.student_id
    JOIN Classes c ON g.student_id = c.student_id
    JOIN Student_Class sc ON c.id = sc.class_id
    JOIN Grades_Scale gs ON c.grade_level = gs.grade_level
    WHERE s.id = ?
    ORDER BY gs.grade_level, su.subject
  """, (student_id,))
  rows = c.fetchall()
  if not rows:
    print("No grades found for this student.")
  else:
    print("\nStudent Grades:")
    for row in rows:
      print(f"Subject: {row[0]}")
      print(f"Grade: {row[1]}")
      print("-" * 30)


def add_attendance():
  """
  Prompts for student ID, date (optional - defaults to current date), and attendance status (present/absent).
  """
  student_id = int(input('Enter student ID: '))
  # ... (existing code to check student existence)
  date = input('Enter date (YYYY-MM-DD) (optional, defaults to today): ') or date.today().strftime('%Y-%m-%d')
  present = input('Enter attendance status (present/absent): ').lower() == 'present'
  c.execute("INSERT INTO Attendance (student_id, date, present) VALUES (?, ?, ?)", (student_id, date, present))
  conn.commit()
  print("Attendance added successfully!")


def view_attendances():
  """
  Displays all attendance records for all students.
  """
  c.execute("""
    SELECT s.name, a.date, a.present
    FROM Students s
    JOIN Attendance a ON s.id = a.student_id
    ORDER BY s.name, a.date
  """)
  rows = c.fetchall()
  if not rows:
    print("No attendance records found.")
  else:
    print("\nAll Attendance Records:")
    for row in rows:
      presence = "Present" if row[2] else "Absent"
      print(f"Student Name: {row[0]}")
      print(f"Date: {row[1]}")
      print(f"Attendance: {presence}")
      print("-" * 30)


def view_student_attendance():
  """
  Displays all attendance records for a specific student.
  """
  student_id = int(input('Enter student ID: '))
  # ... (existing code to check student existence)
  c.execute("SELECT date, present FROM Attendance WHERE student_id = ? ORDER BY date", (student_id,))
  rows = c.fetchall()
  if not rows:
    print("No attendance records found for this student.")
  else:
    print("\nStudent Attendance Records:")
    for row in rows:
      presence = "Present" if row[1] else "Absent"
      print(f"Date: {row[0]}")
      print(f"Attendance: {presence}")
      print("-" * 30)


def add_class():
  """
  Prompts for class name and grade level.
  """
  class_name = input('Enter class name: ')
  grade_level = int(input('Enter grade level (1-6): '))
  if grade_level < 1 or grade_level > 6:
    print("Error: Invalid grade level. Please enter a number between 1 and 6.")
    return
  c.execute("INSERT INTO Classes (class_name, grade_level) VALUES (?, ?)", (class_name, grade_level))
  conn.commit()
  print("Class added successfully!")


def view_classes():
  """
  Displays all classes.
  """
  c.execute("SELECT * FROM Classes")
  rows = c.fetchall()
  if not rows:
    print("No classes found.")
  else:
    print("\nAll Classes:")
    for row in rows:
      print(f"Class ID: {row[0]}")
      print(f"Class Name: {row[1]}")
      print(f"Grade Level: {row[2]}")
      print("-" * 30)


def assign_student_to_class():
  """
  Assigns a student to a class.
  """
  student_id = int(input('Enter student ID: '))
  # ... (existing code to check student existence)
  c.execute("SELECT * FROM Classes")
  classes = c.fetchall()
  if not classes:
    print("No classes available to assign students.")
    return
  print("\nAvailable Classes:")
  for i, row in enumerate(classes):
    print(f"{i+1}. {row[1]} (Grade {row[2]})")
  choice = int(input("Enter choice (number) to assign student: ")) - 1
  if choice < 0 or choice >= len(classes):
    print("Invalid choice.")
    return
  class_id = classes[choice][0]
  c.execute("INSERT INTO Student_Class (student_id, class_id) VALUES (?, ?)", (student_id, class_id))
  conn.commit()
  print("Student assigned to class successfully!")


def view_students_in_class():
  """
  Displays all students enrolled in a specific class.
  """
  c.execute("SELECT * FROM Classes")
  classes = c.fetchall()
  if not classes:
    print("No classes found.")
    return
  print("\nAvailable Classes:")
  for i, row in enumerate(classes):
    print(f"{i+1}. {row[1]} (Grade {row[2]})")
  choice = int(input("Enter choice (number) to view students: ")) - 1
  if choice < 0 or choice >= len(classes):
    print("Invalid choice.")
    return
  class_id = classes[choice][0]
  c.execute("SELECT s.id, s.name FROM Students s JOIN Student_Class sc ON s.id = sc.student_id WHERE sc.class_id = ?", (class_id,))
  rows = c.fetchall()
  if not rows:
    print("No students found in this class.")
  else:
    print("\nStudents Enrolled:")
    for row in rows:
      print(f"Student ID: {row[0]}")
      print(f"Student Name: {row[1]}")
      print("-" * 30)


def export_data_to_csv():
  """
  Exports all student data (including class information) to a CSV file.
  """
  data = []
  c.execute("""
    SELECT s.id, s.name, c.class_name
    FROM Students s
    LEFT JOIN Student_Class sc ON s.id = sc.student_id
    LEFT JOIN Classes c ON sc.class_id = c.id
    ORDER BY s.name, c.class_name
  """)
  rows = c.fetchall()
  data.append(["Student ID", "Student Name", "Class"])
  for row in rows:
    data.append(list(row))

  with open('student_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)
  print("Student data exported to 'student_data.csv' successfully!")


def main():
  """
  Main loop for the school management system.
  """
  while True:
    choice = get_user_choice()
    if choice == 1:
      add_student()
    elif choice == 2:
      view_students()
    elif choice == 3:
      search_students()
    elif choice == 4:
      update_student()
    elif choice == 5:
      delete_student()
    elif choice == 6:
      add_grade()
    elif choice == 7:
      view_grades()
    elif choice == 8:
      view_student_grades()
    elif choice == 9:
      add_attendance()
    elif choice == 10:
      view_attendances()
    elif choice == 11:
      view_student_attendance()
    elif choice == 12:
      # Class Management options
      print("\nClass Management:")
      print("1. Add Class")
      print("2. View Classes")
      print("3. Assign Student to Class")
      print("4. View Students in a Class")
      class_management_choice = int(input("Enter choice (number) for class management: "))
      if class_management_choice == 1:
        add_class()
      elif class_management_choice == 2:
        view_classes()
      elif class_management_choice == 3:
        assign_student_to_class()
      elif class_management_choice == 4:
        view_students_in_class()
      else:
        print("Invalid choice.")
    elif choice == 13:
      export_data_to_csv()
    elif choice == 14:
      print("Exiting School Management System...")
      conn.close()
      break
    else:
      print("Invalid choice. Please try again.")


if __name__ == "__main__":
  main()
