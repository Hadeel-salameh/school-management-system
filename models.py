from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, teacher, student
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    teacher = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')

   def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade_level = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(10), nullable=True)
    academic_year = db.Column(db.String(20), nullable=True, default='2024-2025')
    capacity = db.Column(db.Integer, default=30)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    students = db.relationship('Student', backref='class_', lazy='dynamic')
    subjects = db.relationship('Subject', secondary='class_subjects', backref='classes')
    schedules = db.relationship('Schedule', backref='class_', lazy='dynamic')

    def __repr__(self):
        return f'<Class {self.name}>'


class_subjects = db.Table('class_subjects',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True)
)


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    arabic_name = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    parent_name = db.Column(db.String(100), nullable=True)
    parent_phone = db.Column(db.String(20), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    enrollment_date = db.Column(db.Date, nullable=True)
    profile_image = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    grades = db.relationship('Grade', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    assignments = db.relationship('AssignmentSubmission', backref='student', lazy='dynamic')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def average_grade(self):
        grades = Grade.query.filter_by(student_id=self.id).all()
        if not grades:
            return 0
        total = sum(g.score for g in grades if g.score is not None)
        count = sum(1 for g in grades if g.score is not None)
        return round(total / count, 2) if count > 0 else 0

    @property
    def attendance_percentage(self):
        total = Attendance.query.filter_by(student_id=self.id).count()
        if total == 0:
            return 0
        present = Attendance.query.filter_by(student_id=self.id, status='present').count()
        return round((present / total) * 100, 1)

    def __repr__(self):
        return f'<Student {self.full_name}>'


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    arabic_name = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    hire_date = db.Column(db.Date, nullable=True)
    qualification = db.Column(db.String(200), nullable=True)
    profile_image = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subjects = db.relationship('Subject', backref='teacher', lazy='dynamic')
    grades = db.relationship('Grade', backref='teacher', lazy='dynamic')
    schedules = db.relationship('Schedule', backref='teacher', lazy='dynamic')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'<Teacher {self.full_name}>'


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    total_marks = db.Column(db.Integer, default=100)
    passing_marks = db.Column(db.Integer, default=50)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    grades = db.relationship('Grade', backref='subject', lazy='dynamic', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='subject', lazy='dynamic')
    schedules = db.relationship('Schedule', backref='subject', lazy='dynamic')
    exams = db.relationship('Exam', backref='subject', lazy='dynamic')

    def __repr__(self):
        return f'<Subject {self.name}>'


class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    score = db.Column(db.Float, nullable=True)
    total_score = db.Column(db.Float, default=100)
    exam_type = db.Column(db.String(50), default='نهائي')  # نهائي, منتصف, أسبوعي
    term = db.Column(db.String(20), default='الفصل الأول')
    academic_year = db.Column(db.String(20), default='2024-2025')
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def percentage(self):
        if self.total_score and self.total_score > 0:
            return round((self.score / self.total_score) * 100, 1)
        return 0

    @property
    def letter_grade(self):
        p = self.percentage
        if p >= 95:
            return 'ممتاز+'
        elif p >= 90:
            return 'ممتاز'
        elif p >= 80:
            return 'جيد جداً'
        elif p >= 70:
            return 'جيد'
        elif p >= 60:
            return 'مقبول'
        else:
            return 'راسب'

    @property
    def grade_color(self):
        p = self.percentage
        if p >= 90:
            return 'success'
        elif p >= 80:
            return 'primary'
        elif p >= 70:
            return 'info'
        elif p >= 60:
            return 'warning'
        else:
            return 'danger'

    def __repr__(self):
        return f'<Grade {self.student_id} - {self.subject_id}: {self.score}>'


class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='present')  # present, absent, late, excused
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.date}: {self.status}>'


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    total_marks = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy='dynamic')

    def __repr__(self):
        return f'<Assignment {self.title}>'


class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, submitted, graded

    def __repr__(self):
        return f'<Submission {self.assignment_id} - {self.student_id}>'


class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    exam_date = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.String(10), nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # in minutes
    total_marks = db.Column(db.Integer, default=100)
    exam_type = db.Column(db.String(50), default='نهائي')
    location = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Exam {self.title}>'


class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Sunday, 1=Monday, ...
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    room = db.Column(db.String(50), nullable=True)

    DAY_NAMES = {
        0: 'الأحد',
        1: 'الاثنين',
        2: 'الثلاثاء',
        3: 'الأربعاء',
        4: 'الخميس',
        5: 'الجمعة',
        6: 'السبت'
    }

    @property
    def day_name(self):
        return self.DAY_NAMES.get(self.day_of_week, '')

    def __repr__(self):
        return f'<Schedule {self.class_id} - {self.subject_id}>'


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    target_role = db.Column(db.String(20), default='all')  # all, student, teacher, admin
    is_active = db.Column(db.Boolean, default=True)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship('User', backref='announcements')

    @property
    def short_content(self):
        return self.content[:100] + '...' if len(self.content) > 100 else self.content

    def __repr__(self):
        return f'<Announcement {self.title}>'


class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='عام')
    image_url = db.Column(db.String(500), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='news')

    def __repr__(self):
        return f'<News {self.title}>'


class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), default='رياضي')
    image_url = db.Column(db.String(500), nullable=True)
    activity_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Activity {self.title}>'
