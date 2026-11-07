QA Test Report

School Management System

Project Type: Web-Based School Management System
Testing Type: Manual Software Testing
Application Framework: Python – Flask
Database: SQLAlchemy
Testing Status: Initial Manual Testing Completed

---

1. Project Overview

The School Management System is a web-based application designed to manage school operations, including student records, teacher accounts, academic grades, attendance, assignments, exams, and announcements.

The application supports three user roles:

- Administrator
- Teacher
- Student

2. Testing Objectives

The main objectives were to:

- Verify core application functionality.
- Validate authentication and authorization.
- Test role-based access control.
- Verify student data privacy.
- Check database persistence.
- Test duplicate student record prevention.

3. Test Cases and Results

ID| Test Scenario| Expected Result| Status
TC-01| Login with an incorrect password| Login rejected| PASS
TC-02| Student accesses admin dashboard| Access denied| PASS
TC-03| Teacher accesses admin dashboard| Access denied| PASS
TC-04| Student attempts to modify another student's data| Modification denied| PASS
TC-05| Student attempts to view another student's grades| Access denied| PASS
TC-06| Verify student data after logout and login| Data remains saved| PASS
TC-07| Add a student using an existing student ID| Duplicate record rejected| PASS

4. Testing Techniques

The following manual testing techniques were applied:

- Functional Testing
- Negative Testing
- Authentication Testing
- Authorization Testing
- Role-Based Access Control Testing
- Data Integrity Testing
- Data Persistence Testing

5. Tools and Technologies

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- HTML
- CSS
- Bootstrap
- SQL Database

6. Testing Conclusion

The application successfully passed the initial set of manually executed test cases based on the observed results.

The tested functionality included authentication, access restrictions, student data privacy, data persistence, and duplicate record validation.

Further testing is recommended for performance, browser compatibility, input validation, security vulnerabilities, and comprehensive regression testing.

Prepared by: Hadeel Al-gareeb
Role: Manual QA Tester