Bug Reports & Defect Tracking

School Management System

Project: School Management System
Testing Type: Manual QA Testing
Environment: Localhost
Testing Status: Initial Testing Completed

---

1. Defect Summary

During the initial manual testing phase, no confirmed defects were identified in the tested scenarios.

2. Security and Access Control Observations

Test ID| Scenario| Observed Result| Status
SEC-01| Student attempts to access the Admin Dashboard| Access denied| PASS
SEC-02| Teacher attempts to access the Admin Dashboard| Access denied| PASS
SEC-03| Student attempts to modify another student's data| Modification prevented| PASS
SEC-04| Student attempts to access another student's grades| Access prevented| PASS

3. Data Integrity Observations

Test ID| Scenario| Observed Result| Status
DATA-01| Student record persistence after logout and login| Record remained saved| PASS
DATA-02| Duplicate student ID validation| Duplicate record rejected| PASS

4. Authentication Observation

Test ID| Scenario| Observed Result| Status
AUTH-01| Login using an incorrect password| Login rejected| PASS

5. Confirmed Defects

No confirmed defects were identified during the executed test cases.

6. Recommendations

- Perform additional exploratory testing.
- Test input validation with invalid and unexpected values.
- Perform browser compatibility testing.
- Conduct performance and security testing.
- Document any future defects with reproducible steps and screenshots.

Prepared by: Hadeel Al-gareeb