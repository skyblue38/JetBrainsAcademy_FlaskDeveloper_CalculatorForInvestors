# Please, don't modify
id = 19
full_name = "Percy"
email = "percy@gmail.com"
gpa = 9.2

dept_name = input()
cursor.execute('SELECT * FROM Department WHERE name = ?', (dept_name,))
dept = cursor.fetchone()
dept_id = dept[0]
new_student = (id, full_name, email, gpa, dept_id)
cursor.execute("INSERT INTO Student(id, full_name, email, GPA, department) VALUES (?,?,?,?,?)",
               new_student)
con.commit()
