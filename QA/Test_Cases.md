# Manual QA Test Cases
## School Management System

Project: School Management System  
Testing Type: Manual Testing  
Test Environment: Localhost  
Testing Status: Completed Initial Testing  

---

## 1. Authentication Testing

### TC-001: Login with Invalid Password

**Preconditions:**
- User account exists.

**Test Steps:**
1. Open the login page.
2. Enter a valid username.
3. Enter an incorrect password.
4. Click the Login button.

**Expected Result:**
- Login should be rejected.
- An appropriate error message should be displayed.

**Actual Result:**
- Login was rejected successfully.
- The system displayed an error message.

**Status:** PASS

**Evidence:**
- `Screenshots/01_Invalid_Login.png`

---

## 2. Authorization Testing

### TC-002: Student Access to Admin Dashboard

**Preconditions:**
- A student account exists.

**Test Steps:**
1. Log in as a student.
2. Open the admin dashboard URL directly.

**Expected Result:**
- Access should be denied.
- The student should not be able to access admin functions.

**Actual Result:**
- Access was denied with a permission message.

**Status:** PASS

**Evidence:**
- `Screenshots/02_Student_Access_Denied.png`

---

### TC-003: Teacher Access to Admin Dashboard

**Preconditions:**
- A teacher account exists.

**Test Steps:**
1. Log in as a teacher.
2. Open the admin dashboard URL directly.

**Expected Result:**
- Access should be denied.
- The teacher should not be able to access admin functions.

**Actual Result:**
- Access was denied with a permission message.

**Status:** PASS

**Evidence:**
- `Screenshots/03_Teacher_Access_Denied.png`

---

## 3. Data Security Testing

### TC-004: Prevent Unauthorized Student Data Modification

**Preconditions:**
- A student account exists.
- Another student's record exists.

**Test Steps:**
1. Log in as a student.
2. Attempt to modify another student's information.

**Expected Result:**
- Unauthorized modification should be prevented.

**Actual Result:**
- Modification was prevented.

**Status:** PASS

**Evidence:**
- No dedicated screenshot available.

---

### TC-005: Prevent Unauthorized Grade Access

**Preconditions:**
- A student account exists.
- Another student's grades exist.

**Test Steps:**
1. Log in as a student.
2. Open the grades page.
3. Attempt to access another student's grades.

**Expected Result:**
- Only the logged-in student's grades should be accessible.
- Access to other students' grades should be denied.

**Actual Result:**
- Access to other students' grades was prevented.

**Status:** PASS

**Evidence:**
- `Screenshots/04_Student_Grades.png`
- This screenshot documents the student grades page.
- A separate screenshot of the denied unauthorized access is not available.

---

## 4. Database Testing

### TC-006: Data Persistence

**Preconditions:**
- Administrator account exists.

**Test Steps:**
1. Log in as an administrator.
2. Add a new student.
3. Save the student record.
4. Log out.
5. Log in again.
6. Check the student list.

**Expected Result:**
- Student information should remain saved after logging out and logging in again.

**Actual Result:**
- The student record remained available in the student list.

**Status:** PASS

**Evidence:**
- `Screenshots/07_Saved_Student_Record.png`

---

### TC-007: Duplicate Student ID Validation

**Preconditions:**
- At least one student record already exists.

**Test Steps:**
1. Open the Add Student page.
2. Enter an existing student ID.
3. Enter different student details.
4. Attempt to save the student.

**Expected Result:**
- The system should reject duplicate student IDs.
- An appropriate validation message should be displayed.

**Actual Result:**
- The system rejected the duplicate student ID and displayed an error message.

**Status:** PASS

**Evidence:**
- `Screenshots/08_Duplicate_Student_ID.png`

---

## 5. Additional Application Screenshots

The following screenshots document important application interfaces:

| Screenshot | Description |
|---|---|
| `05_Admin_Dashboard.png` | Admin dashboard interface |
| `06_Add_New_Student.png` | Add new student form |

---

## 6. Testing Summary

| Metric | Result |
|---|---:|
| Total Test Cases | 7 |
| Passed | 7 |
| Failed | 0 |
| Pending | 0 |

### Final Result

All seven manually executed test cases passed according to the recorded test results.

The testing covered:
- Authentication
- Role-based authorization
- Data security
- Database persistence
- Duplicate student ID validation

### Recommendations for Further Testing

Further testing is recommended for:
- Performance testing
- Cross-browser compatibility
- Input validation
- Security vulnerabilities
- Additional user permission scenarios

---
Prepared by: Hadeel Al-gareeb
Role: Manual QA Tester