from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from functools import wraps
from datetime import datetime, date
import os

from config import Config
from models import (db, User, Student, Teacher, Subject, Class, Grade,
                    Attendance, Assignment, AssignmentSubmission, Exam,
                    Schedule, Announcement, News, Activity)
from forms import (LoginForm, StudentForm, TeacherForm, ClassForm, SubjectForm,
                   GradeForm, AttendanceForm, AnnouncementForm, ExamForm,
                   AssignmentForm, UserForm, ContactForm)

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)

# Ensure instance folder exists
os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'الرجاء تسجيل الدخول للوصول إلى هذه الصفحة'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Role Decorators ─────────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['teacher', 'admin']:
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ─── Context Processors ───────────────────────────────────────────────────────

@app.context_processor
def inject_globals():
    announcements = []
    if current_user.is_authenticated:
        announcements = Announcement.query.filter(
            (Announcement.target_role == 'all') |
            (Announcement.target_role == current_user.role)
        ).filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(5).all()

    return dict(
        school_name=app.config['SCHOOL_NAME'],
        school_motto=app.config['SCHOOL_MOTTO'],
        current_year=datetime.now().year,
        global_announcements=announcements,
        csrf_token=generate_csrf
    )


# ─── Public Routes ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    news_list = News.query.filter_by(is_published=True).order_by(News.created_at.desc()).limit(3).all()
    activities_list = Activity.query.filter_by(is_active=True).order_by(Activity.created_at.desc()).limit(4).all()

    stats = {
        'students': Student.query.filter_by(is_active=True).count(),
        'teachers': Teacher.query.filter_by(is_active=True).count(),
        'classes': Class.query.count(),
        'subjects': Subject.query.filter_by(is_active=True).count(),
    }

    return render_template(
        'index.html',
        news_list=news_list,
        activities_list=activities_list,
        stats=stats
    )


@app.route('/about')
def about():
    teachers_count = Teacher.query.filter_by(is_active=True).count()
    students_count = Student.query.filter_by(is_active=True).count()

    return render_template(
        'about.html',
        teachers_count=teachers_count,
        students_count=students_count
    )


@app.route('/teachers')
def teachers_page():
    teachers = Teacher.query.filter_by(is_active=True).all()
    return render_template('teachers.html', teachers=teachers)


@app.route('/news')
def news_page():
    category = request.args.get('category', 'all')

    if category == 'all':
        news_list = News.query.filter_by(
            is_published=True
        ).order_by(News.created_at.desc()).all()
    else:
        news_list = News.query.filter_by(
            is_published=True,
            category=category
        ).order_by(News.created_at.desc()).all()

    return render_template(
        'news.html',
        news_list=news_list,
        active_category=category
    )


@app.route('/activities')
def activities_page():
    category = request.args.get('category', 'الكل')

    if category == 'الكل':
        activities = Activity.query.filter_by(
            is_active=True
        ).order_by(Activity.created_at.desc()).all()
    else:
        activities = Activity.query.filter_by(
            is_active=True,
            category=category
        ).order_by(Activity.created_at.desc()).all()

    return render_template(
        'activities.html',
        activities=activities,
        active_category=category
    )


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        flash('تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html', form=form)


# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_redirect'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            if user.role != form.role.data:
                flash('نوع المستخدم غير مطابق لاسم المستخدم المدخل', 'danger')
                return render_template('login.html', form=form)

            if not user.is_active:
                flash('حسابك غير نشط. الرجاء التواصل مع الإدارة.', 'warning')
                return render_template('login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()

            flash(f'مرحباً بك، {user.username}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            return redirect(url_for('dashboard_redirect'))

        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard_redirect():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('student_dashboard'))

    return redirect(url_for('index'))


# ─── Student Routes ───────────────────────────────────────────────────────────

@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()

    grades = Grade.query.filter_by(
        student_id=student.id
    ).order_by(Grade.created_at.desc()).limit(5).all()

    announcements = Announcement.query.filter(
        (Announcement.target_role == 'all') |
        (Announcement.target_role == 'student')
    ).filter_by(
        is_active=True
    ).order_by(Announcement.created_at.desc()).limit(5).all()

    schedule = []
    if student.class_id:
        schedule = Schedule.query.filter_by(
            class_id=student.class_id
        ).order_by(
            Schedule.day_of_week,
            Schedule.start_time
        ).all()

    assignments = Assignment.query.filter_by(
        class_id=student.class_id,
        is_active=True
    ).order_by(Assignment.due_date).limit(5).all()

    attendance_total = Attendance.query.filter_by(student_id=student.id).count()
    attendance_present = Attendance.query.filter_by(
        student_id=student.id,
        status='present'
    ).count()

    return render_template(
        'student/dashboard.html',
        student=student,
        grades=grades,
        announcements=announcements,
        schedule=schedule,
        assignments=assignments,
        attendance_total=attendance_total,
        attendance_present=attendance_present
    )


@app.route('/student/profile')
@login_required
@student_required
def student_profile():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    return render_template('student/profile.html', student=student)


@app.route('/student/grades')
@login_required
@student_required
def student_grades():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    term = request.args.get('term', 'الفصل الأول')

    grades = Grade.query.filter_by(
        student_id=student.id,
        term=term
    ).all()

    all_grades = Grade.query.filter_by(student_id=student.id).all()

    return render_template(
        'student/grades.html',
        student=student,
        grades=grades,
        all_grades=all_grades,
        active_term=term
    )


@app.route('/student/attendance')
@login_required
@student_required
def student_attendance():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()

    attendances = Attendance.query.filter_by(
        student_id=student.id
    ).order_by(Attendance.date.desc()).all()

    return render_template(
        'student/attendance.html',
        student=student,
        attendances=attendances
    )


@app.route('/student/schedule')
@login_required
@student_required
def student_schedule():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()

    schedule = []
    if student.class_id:
        schedule = Schedule.query.filter_by(
            class_id=student.class_id
        ).order_by(
            Schedule.day_of_week,
            Schedule.start_time
        ).all()

    return render_template(
        'student/schedule.html',
        student=student,
        schedule=schedule
    )


@app.route('/student/assignments')
@login_required
@student_required
def student_assignments():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()

    assignments = Assignment.query.filter_by(
        class_id=student.class_id,
        is_active=True
    ).order_by(Assignment.due_date).all()

    return render_template(
        'student/assignments.html',
        student=student,
        assignments=assignments
    )


@app.route('/student/reports')
@login_required
@student_required
def student_reports():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    grades = Grade.query.filter_by(student_id=student.id).all()

    return render_template(
        'student/reports.html',
        student=student,
        grades=grades
    )


# ─── Teacher Routes ───────────────────────────────────────────────────────────

@app.route('/teacher/dashboard')
@login_required
@teacher_required
def teacher_dashboard():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()

    if not teacher and current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))

    if not teacher:
        flash('لم يتم ربط حسابك بملف معلم. الرجاء التواصل مع الإدارة.', 'warning')
        return redirect(url_for('index'))

    subjects = Subject.query.filter_by(teacher_id=teacher.id).all()

    classes_ids = set()
    for subject in subjects:
        for cls in subject.classes:
            classes_ids.add(cls.id)

    classes_count = len(classes_ids)

    students_count = Student.query.filter(
        Student.class_id.in_(list(classes_ids))
    ).count() if classes_ids else 0

    assignments = Assignment.query.filter(
        Assignment.subject_id.in_([s.id for s in subjects])
    ).order_by(Assignment.due_date).limit(5).all()

    schedule = Schedule.query.filter_by(
        teacher_id=teacher.id
    ).order_by(
        Schedule.day_of_week,
        Schedule.start_time
    ).all()

    recent_grades = Grade.query.filter_by(
        teacher_id=teacher.id
    ).order_by(Grade.created_at.desc()).limit(10).all()

    return render_template(
        'teacher/dashboard.html',
        teacher=teacher,
        subjects=subjects,
        classes_count=classes_count,
        students_count=students_count,
        assignments=assignments,
        schedule=schedule,
        recent_grades=recent_grades
    )


@app.route('/teacher/students')
@login_required
@teacher_required
def teacher_students():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first_or_404()
    subjects = Subject.query.filter_by(teacher_id=teacher.id).all()

    classes_ids = set()
    for subject in subjects:
        for cls in subject.classes:
            classes_ids.add(cls.id)

    students = Student.query.filter(
        Student.class_id.in_(list(classes_ids))
    ).all() if classes_ids else []

    return render_template(
        'teacher/students.html',
        teacher=teacher,
        students=students
    )


@app.route('/teacher/grades', methods=['GET', 'POST'])
@login_required
@teacher_required
def teacher_grades():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first_or_404()
    subjects = Subject.query.filter_by(teacher_id=teacher.id).all()

    form = GradeForm()
    form.subject_id.choices = [(0, 'اختر المادة')] + [
        (s.id, s.name) for s in subjects
    ]

    all_students = Student.query.filter_by(is_active=True).all()
    form.student_id.choices = [(0, 'اختر الطالب')] + [
        (s.id, s.full_name) for s in all_students
    ]

    if form.validate_on_submit():
        grade = Grade(
            student_id=form.student_id.data,
            subject_id=form.subject_id.data,
            teacher_id=teacher.id,
            score=form.score.data,
            total_score=form.total_score.data or 100,
            exam_type=form.exam_type.data,
            term=form.term.data,
            academic_year=form.academic_year.data or '2024-2025',
            remarks=form.remarks.data
        )

        db.session.add(grade)
        db.session.commit()

        flash('تم إضافة الدرجة بنجاح', 'success')
        return redirect(url_for('teacher_grades'))

    grades = Grade.query.filter_by(
        teacher_id=teacher.id
    ).order_by(Grade.created_at.desc()).limit(50).all()

    return render_template(
        'teacher/grades.html',
        teacher=teacher,
        form=form,
        grades=grades
    )


@app.route('/teacher/attendance', methods=['GET', 'POST'])
@login_required
@teacher_required
def teacher_attendance():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first_or_404()
    subjects = Subject.query.filter_by(teacher_id=teacher.id).all()

    form = AttendanceForm()

    all_students = Student.query.filter_by(is_active=True).all()
    form.student_id.choices = [(0, 'اختر الطالب')] + [
        (s.id, s.full_name) for s in all_students
    ]

    form.subject_id.choices = [(0, 'اختر المادة')] + [
        (s.id, s.name) for s in subjects
    ]

    if form.validate_on_submit():
        attendance = Attendance(
            student_id=form.student_id.data,
            subject_id=form.subject_id.data if form.subject_id.data else None,
            date=form.date.data,
            status=form.status.data,
            notes=form.notes.data
        )

        db.session.add(attendance)
        db.session.commit()

        flash('تم تسجيل الحضور بنجاح', 'success')
        return redirect(url_for('teacher_attendance'))

    attendances = Attendance.query.order_by(
        Attendance.date.desc()
    ).limit(30).all()

    return render_template(
        'teacher/attendance.html',
        teacher=teacher,
        form=form,
        attendances=attendances
    )


@app.route('/teacher/assignments', methods=['GET', 'POST'])
@login_required
@teacher_required
def teacher_assignments():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first_or_404()
    subjects = Subject.query.filter_by(teacher_id=teacher.id).all()

    form = AssignmentForm()
    form.subject_id.choices = [(0, 'اختر المادة')] + [
        (s.id, s.name) for s in subjects
    ]

    classes = Class.query.all()
    form.class_id.choices = [(0, 'جميع الصفوف')] + [
        (c.id, c.name) for c in classes
    ]

    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            subject_id=form.subject_id.data,
            class_id=form.class_id.data if form.class_id.data else None,
            due_date=form.due_date.data,
            total_marks=form.total_marks.data or 10
        )

        db.session.add(assignment)
        db.session.commit()

        flash('تم إضافة الواجب بنجاح', 'success')
        return redirect(url_for('teacher_assignments'))

    assignments = Assignment.query.filter(
        Assignment.subject_id.in_([s.id for s in subjects])
    ).order_by(Assignment.due_date.desc()).all()

    return render_template(
        'teacher/assignments.html',
        teacher=teacher,
        form=form,
        assignments=assignments
    )


@app.route('/teacher/exams', methods=['GET', 'POST'])
@login_required
@teacher_required
def teacher_exams():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first_or_404()
    subjects = Subject.query.filter_by(teacher_id=teacher.id).all()

    form = ExamForm()
    form.subject_id.choices = [(0, 'اختر المادة')] + [
        (s.id, s.name) for s in subjects
    ]

    classes = Class.query.all()
    form.class_id.choices = [(0, 'جميع الصفوف')] + [
        (c.id, c.name) for c in classes
    ]

    if form.validate_on_submit():
        exam = Exam(
            title=form.title.data,
            subject_id=form.subject_id.data,
            class_id=form.class_id.data if form.class_id.data else None,
            exam_date=form.exam_date.data,
            start_time=form.start_time.data,
            duration=form.duration.data,
            total_marks=form.total_marks.data or 100,
            exam_type=form.exam_type.data,
            location=form.location.data,
            description=form.description.data
        )

        db.session.add(exam)
        db.session.commit()

        flash('تم إضافة الاختبار بنجاح', 'success')
        return redirect(url_for('teacher_exams'))

    exams = Exam.query.filter(
        Exam.subject_id.in_([s.id for s in subjects])
    ).order_by(Exam.exam_date.desc()).all()

    return render_template(
        'teacher/exams.html',
        teacher=teacher,
        form=form,
        exams=exams
    )


# ─── Admin Routes ─────────────────────────────────────────────────────────────

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'students': Student.query.filter_by(is_active=True).count(),
        'teachers': Teacher.query.filter_by(is_active=True).count(),
        'classes': Class.query.count(),
        'subjects': Subject.query.filter_by(is_active=True).count(),
        'users': User.query.count(),
    }

    recent_students = Student.query.order_by(
        Student.created_at.desc()
    ).limit(5).all()

    recent_announcements = Announcement.query.order_by(
        Announcement.created_at.desc()
    ).limit(5).all()

    total_attendance = Attendance.query.count()
    present_attendance = Attendance.query.filter_by(status='present').count()

    attendance_pct = round(
        (present_attendance / total_attendance * 100), 1
    ) if total_attendance > 0 else 0

    classes = Class.query.all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_students=recent_students,
        recent_announcements=recent_announcements,
        attendance_pct=attendance_pct,
        classes=classes
    )


# ─── Admin Students CRUD ──────────────────────────────────────────────────────

@app.route('/admin/students')
@login_required
@admin_required
def admin_students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Student.query

    if search:
        query = query.filter(
            (Student.first_name.ilike(f'%{search}%')) |
            (Student.last_name.ilike(f'%{search}%')) |
            (Student.student_id.ilike(f'%{search}%'))
        )

    students = query.order_by(
        Student.created_at.desc()
    ).paginate(page=page, per_page=15)

    return render_template(
        'admin/students.html',
        students=students,
        search=search
    )


# تم تصحيح هذه الدالة وإزالة التكرار ومشكلة المسافات البادئة
@app.route('/admin/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_student_add():
    form = StudentForm()

    classes = Class.query.order_by(Class.name).all()
    form.class_id.choices = [(0, 'اختر الصف')] + [
        (c.id, c.name) for c in classes
    ]

    if form.validate_on_submit():
        student_id = (form.student_id.data or '').strip()
        username = (form.username.data or '').strip()
        email = (form.email.data or '').strip() or None

        # التحقق من الرقم الطلابي
        if Student.query.filter_by(student_id=student_id).first():
            flash('الرقم الطلابي مستخدم بالفعل', 'danger')

        # التحقق من اسم المستخدم
        elif User.query.filter_by(username=username).first():
            flash('اسم المستخدم مستخدم بالفعل', 'danger')

        # التحقق من البريد الإلكتروني
        elif email and User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني مستخدم بالفعل', 'danger')

        else:
            try:
                # إنشاء حساب المستخدم
                user = User(
                    username=username,
                    email=email,
                    role='student',
                    is_active=True
                )

                user.set_password(form.password.data or student_id)

                db.session.add(user)
                db.session.flush()

                # إنشاء ملف الطالب وربطه بحساب المستخدم
                student = Student(
                    user_id=user.id,
                    student_id=student_id,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    arabic_name=form.arabic_name.data,
                    date_of_birth=form.date_of_birth.data,
                    gender=form.gender.data,
                    phone=form.phone.data,
                    address=form.address.data,
                    parent_name=form.parent_name.data,
                    parent_phone=form.parent_phone.data,
                    class_id=form.class_id.data or None,
                    enrollment_date=form.enrollment_date.data,
                    is_active=True
                )

                db.session.add(student)
                db.session.commit()

                flash('تمت إضافة الطالب بنجاح', 'success')
                return redirect(url_for('admin_students'))

            except Exception:
                db.session.rollback()
                app.logger.exception('Error while adding student')
                flash(
                    'حدث خطأ أثناء إضافة الطالب، يرجى المحاولة مرة أخرى.',
                    'danger'
                )

    return render_template(
        'admin/student_form.html',
        form=form,
        title='إضافة طالب جديد'
    )


@app.route('/admin/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_student_edit(id):
    student = Student.query.get_or_404(id)

    form = StudentForm(obj=student)
    classes = Class.query.all()

    form.class_id.choices = [(0, 'اختر الصف')] + [
        (c.id, c.name) for c in classes
    ]

    if request.method == 'GET':
        form.username.data = student.user.username
        form.email.data = student.user.email
        form.class_id.data = student.class_id or 0

    if form.validate_on_submit():
        student.user.username = form.username.data
        student.user.email = form.email.data

        if form.password.data:
            student.user.set_password(form.password.data)

        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.arabic_name = form.arabic_name.data
        student.student_id = form.student_id.data
        student.date_of_birth = form.date_of_birth.data
        student.gender = form.gender.data
        student.phone = form.phone.data
        student.address = form.address.data
        student.parent_name = form.parent_name.data
        student.parent_phone = form.parent_phone.data
        student.class_id = form.class_id.data if form.class_id.data else None
        student.enrollment_date = form.enrollment_date.data

        db.session.commit()

        flash('تم تحديث بيانات الطالب بنجاح', 'success')
        return redirect(url_for('admin_students'))

    return render_template(
        'admin/student_form.html',
        form=form,
        student=student,
        title='تعديل بيانات الطالب'
    )


@app.route('/admin/students/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_student_delete(id):
    student = Student.query.get_or_404(id)
    user = student.user

    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()

    flash('تم حذف الطالب بنجاح', 'success')
    return redirect(url_for('admin_students'))


# ─── Admin Teachers CRUD ──────────────────────────────────────────────────────

@app.route('/admin/teachers')
@login_required
@admin_required
def admin_teachers():
    search = request.args.get('search', '')
    query = Teacher.query

    if search:
        query = query.filter(
            (Teacher.first_name.ilike(f'%{search}%')) |
            (Teacher.last_name.ilike(f'%{search}%')) |
            (Teacher.teacher_id.ilike(f'%{search}%'))
        )

    teachers = query.order_by(Teacher.created_at.desc()).all()

    return render_template(
        'admin/teachers.html',
        teachers=teachers,
        search=search
    )


@app.route('/admin/teachers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_teacher_add():
    form = TeacherForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('اسم المستخدم مستخدم بالفعل', 'danger')
            return render_template(
                'admin/teacher_form.html',
                form=form,
                title='إضافة معلم جديد'
            )

        user = User(
            username=form.username.data,
            email=form.email.data,
            role='teacher'
        )

        user.set_password(form.password.data or form.teacher_id.data)

        db.session.add(user)
        db.session.flush()

        teacher = Teacher(
            user_id=user.id,
            teacher_id=form.teacher_id.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            arabic_name=form.arabic_name.data,
            specialization=form.specialization.data,
            phone=form.phone.data,
            address=form.address.data,
            hire_date=form.hire_date.data,
            qualification=form.qualification.data,
            bio=form.bio.data
        )

        db.session.add(teacher)
        db.session.commit()

        flash('تم إضافة المعلم بنجاح', 'success')
        return redirect(url_for('admin_teachers'))

    return render_template(
        'admin/teacher_form.html',
        form=form,
        title='إضافة معلم جديد'
    )


@app.route('/admin/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_teacher_edit(id):
    teacher = Teacher.query.get_or_404(id)

    form = TeacherForm(obj=teacher)

    if request.method == 'GET':
        form.username.data = teacher.user.username
        form.email.data = teacher.user.email

    if form.validate_on_submit():
        teacher.user.username = form.username.data
        teacher.user.email = form.email.data

        if form.password.data:
            teacher.user.set_password(form.password.data)

        teacher.first_name = form.first_name.data
        teacher.last_name = form.last_name.data
        teacher.arabic_name = form.arabic_name.data
        teacher.teacher_id = form.teacher_id.data
        teacher.specialization = form.specialization.data
        teacher.phone = form.phone.data
        teacher.address = form.address.data
        teacher.hire_date = form.hire_date.data
        teacher.qualification = form.qualification.data
        teacher.bio = form.bio.data

        db.session.commit()

        flash('تم تحديث بيانات المعلم بنجاح', 'success')
        return redirect(url_for('admin_teachers'))

    return render_template(
        'admin/teacher_form.html',
        form=form,
        teacher=teacher,
        title='تعديل بيانات المعلم'
    )


@app.route('/admin/teachers/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_teacher_delete(id):
    teacher = Teacher.query.get_or_404(id)
    user = teacher.user

    db.session.delete(teacher)
    db.session.delete(user)
    db.session.commit()

    flash('تم حذف المعلم بنجاح', 'success')
    return redirect(url_for('admin_teachers'))


# ─── Admin Classes CRUD ───────────────────────────────────────────────────────

@app.route('/admin/classes')
@login_required
@admin_required
def admin_classes():
    classes = Class.query.all()
    return render_template('admin/classes.html', classes=classes)


@app.route('/admin/classes/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_class_add():
    form = ClassForm()

    if form.validate_on_submit():
        cls = Class(
            name=form.name.data,
            grade_level=form.grade_level.data,
            section=form.section.data,
            academic_year=form.academic_year.data,
            capacity=form.capacity.data,
            description=form.description.data
        )

        db.session.add(cls)
        db.session.commit()

        flash('تم إضافة الصف بنجاح', 'success')
        return redirect(url_for('admin_classes'))

    return render_template(
        'admin/class_form.html',
        form=form,
        title='إضافة صف جديد'
    )


@app.route('/admin/classes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_class_edit(id):
    cls = Class.query.get_or_404(id)
    form = ClassForm(obj=cls)

    if form.validate_on_submit():
        cls.name = form.name.data
        cls.grade_level = form.grade_level.data
        cls.section = form.section.data
        cls.academic_year = form.academic_year.data
        cls.capacity = form.capacity.data
        cls.description = form.description.data

        db.session.commit()

        flash('تم تحديث الصف بنجاح', 'success')
        return redirect(url_for('admin_classes'))

    return render_template(
        'admin/class_form.html',
        form=form,
        cls=cls,
        title='تعديل بيانات الصف'
    )


@app.route('/admin/classes/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_class_delete(id):
    cls = Class.query.get_or_404(id)

    db.session.delete(cls)
    db.session.commit()

    flash('تم حذف الصف بنجاح', 'success')
    return redirect(url_for('admin_classes'))


# ─── Admin Subjects CRUD ──────────────────────────────────────────────────────

@app.route('/admin/subjects')
@login_required
@admin_required
def admin_subjects():
    subjects = Subject.query.filter_by(is_active=True).all()
    return render_template('admin/subjects.html', subjects=subjects)


@app.route('/admin/subjects/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_subject_add():
    form = SubjectForm()

    teachers = Teacher.query.filter_by(is_active=True).all()
    form.teacher_id.choices = [(0, 'بدون معلم')] + [
        (t.id, t.full_name) for t in teachers
    ]

    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            name_en=form.name_en.data,
            code=form.code.data,
            teacher_id=form.teacher_id.data if form.teacher_id.data else None,
            total_marks=form.total_marks.data or 100,
            passing_marks=form.passing_marks.data or 50,
            description=form.description.data
        )

        db.session.add(subject)
        db.session.commit()

        flash('تم إضافة المادة بنجاح', 'success')
        return redirect(url_for('admin_subjects'))

    return render_template(
        'admin/subject_form.html',
        form=form,
        title='إضافة مادة جديدة'
    )


@app.route('/admin/subjects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_subject_edit(id):
    subject = Subject.query.get_or_404(id)
    form = SubjectForm(obj=subject)

    teachers = Teacher.query.filter_by(is_active=True).all()
    form.teacher_id.choices = [(0, 'بدون معلم')] + [
        (t.id, t.full_name) for t in teachers
    ]

    if request.method == 'GET':
        form.teacher_id.data = subject.teacher_id or 0

    if form.validate_on_submit():
        subject.name = form.name.data
        subject.name_en = form.name_en.data
        subject.code = form.code.data
        subject.teacher_id = form.teacher_id.data if form.teacher_id.data else None
        subject.total_marks = form.total_marks.data or 100
        subject.passing_marks = form.passing_marks.data or 50
        subject.description = form.description.data

        db.session.commit()

        flash('تم تحديث المادة بنجاح', 'success')
        return redirect(url_for('admin_subjects'))

    return render_template(
        'admin/subject_form.html',
        form=form,
        subject=subject,
        title='تعديل المادة'
    )


@app.route('/admin/subjects/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_subject_delete(id):
    subject = Subject.query.get_or_404(id)
    subject.is_active = False

    db.session.commit()

    flash('تم حذف المادة بنجاح', 'success')
    return redirect(url_for('admin_subjects'))


# ─── Admin Grades CRUD ────────────────────────────────────────────────────────

@app.route('/admin/grades')
@login_required
@admin_required
def admin_grades():
    page = request.args.get('page', 1, type=int)

    grades = Grade.query.order_by(
        Grade.created_at.desc()
    ).paginate(page=page, per_page=20)

    return render_template('admin/grades.html', grades=grades)


@app.route('/admin/grades/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_grade_add():
    form = GradeForm()

    students = Student.query.filter_by(is_active=True).all()
    subjects = Subject.query.filter_by(is_active=True).all()

    form.student_id.choices = [(0, 'اختر الطالب')] + [
        (s.id, s.full_name) for s in students
    ]

    form.subject_id.choices = [(0, 'اختر المادة')] + [
        (s.id, s.name) for s in subjects
    ]

    if form.validate_on_submit():
        grade = Grade(
            student_id=form.student_id.data,
            subject_id=form.subject_id.data,
            score=form.score.data,
            total_score=form.total_score.data or 100,
            exam_type=form.exam_type.data,
            term=form.term.data,
            academic_year=form.academic_year.data or '2024-2025',
            remarks=form.remarks.data
        )

        db.session.add(grade)
        db.session.commit()

        flash('تم إضافة الدرجة بنجاح', 'success')
        return redirect(url_for('admin_grades'))

    return render_template(
        'admin/grade_form.html',
        form=form,
        title='إضافة درجة جديدة'
    )


@app.route('/admin/grades/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_grade_edit(id):
    grade = Grade.query.get_or_404(id)
    form = GradeForm(obj=grade)

    students = Student.query.filter_by(is_active=True).all()
    subjects = Subject.query.filter_by(is_active=True).all()

    form.student_id.choices = [(0, 'اختر الطالب')] + [
        (s.id, s.full_name) for s in students
    ]

    form.subject_id.choices = [(0, 'اختر المادة')] + [
        (s.id, s.name) for s in subjects
    ]

    if form.validate_on_submit():
        grade.student_id = form.student_id.data
        grade.subject_id = form.subject_id.data
        grade.score = form.score.data
        grade.total_score = form.total_score.data or 100
        grade.exam_type = form.exam_type.data
        grade.term = form.term.data
        grade.remarks = form.remarks.data

        db.session.commit()

        flash('تم تحديث الدرجة بنجاح', 'success')
        return redirect(url_for('admin_grades'))

    return render_template(
        'admin/grade_form.html',
        form=form,
        grade=grade,
        title='تعديل الدرجة'
    )


@app.route('/admin/grades/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_grade_delete(id):
    grade = Grade.query.get_or_404(id)

    db.session.delete(grade)
    db.session.commit()

    flash('تم حذف الدرجة بنجاح', 'success')
    return redirect(url_for('admin_grades'))


# ─── Admin Attendance CRUD ────────────────────────────────────────────────────

@app.route('/admin/attendance')
@login_required
@admin_required
def admin_attendance():
    page = request.args.get('page', 1, type=int)

    attendances = Attendance.query.order_by(
        Attendance.date.desc()
    ).paginate(page=page, per_page=20)

    return render_template(
        'admin/attendance.html',
        attendances=attendances
    )


@app.route('/admin/attendance/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_attendance_add():
    form = AttendanceForm()

    students = Student.query.filter_by(is_active=True).all()
    subjects = Subject.query.filter_by(is_active=True).all()

    form.student_id.choices = [(0, 'اختر الطالب')] + [
        (s.id, s.full_name) for s in students
    ]

    form.subject_id.choices = [(0, 'اختر المادة')] + [
        (s.id, s.name) for s in subjects
    ]

    if form.validate_on_submit():
        att = Attendance(
            student_id=form.student_id.data,
            subject_id=form.subject_id.data if form.subject_id.data else None,
            date=form.date.data,
            status=form.status.data,
            notes=form.notes.data
        )

        db.session.add(att)
        db.session.commit()

        flash('تم تسجيل الحضور بنجاح', 'success')
        return redirect(url_for('admin_attendance'))

    return render_template(
        'admin/attendance_form.html',
        form=form,
        title='تسجيل حضور جديد'
    )


@app.route('/admin/attendance/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_attendance_delete(id):
    att = Attendance.query.get_or_404(id)

    db.session.delete(att)
    db.session.commit()

    flash('تم حذف سجل الحضور بنجاح', 'success')
    return redirect(url_for('admin_attendance'))


# ─── Admin Exams ──────────────────────────────────────────────────────────────

@app.route('/admin/exams')
@login_required
@admin_required
def admin_exams():
    exams = Exam.query.order_by(Exam.exam_date.desc()).all()
    return render_template('admin/exams.html', exams=exams)


@app.route('/admin/exams/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_exam_add():
    form = ExamForm()

    subjects = Subject.query.filter_by(is_active=True).all()
    classes = Class.query.all()

    form.subject_id.choices = [(0, 'اختر المادة')] + [
        (s.id, s.name) for s in subjects
    ]

    form.class_id.choices = [(0, 'جميع الصفوف')] + [
        (c.id, c.name) for c in classes
    ]

    if form.validate_on_submit():
        exam = Exam(
            title=form.title.data,
            subject_id=form.subject_id.data,
            class_id=form.class_id.data if form.class_id.data else None,
            exam_date=form.exam_date.data,
            start_time=form.start_time.data,
            duration=form.duration.data,
            total_marks=form.total_marks.data or 100,
            exam_type=form.exam_type.data,
            location=form.location.data,
            description=form.description.data
        )

        db.session.add(exam)
        db.session.commit()

        flash('تم إضافة الاختبار بنجاح', 'success')
        return redirect(url_for('admin_exams'))

    return render_template(
        'admin/exam_form.html',
        form=form,
        title='إضافة اختبار جديد'
    )


@app.route('/admin/exams/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_exam_delete(id):
    exam = Exam.query.get_or_404(id)

    db.session.delete(exam)
    db.session.commit()

    flash('تم حذف الاختبار بنجاح', 'success')
    return redirect(url_for('admin_exams'))


# ─── Admin Announcements CRUD ─────────────────────────────────────────────────

@app.route('/admin/announcements')
@login_required
@admin_required
def admin_announcements():
    announcements = Announcement.query.order_by(
        Announcement.created_at.desc()
    ).all()

    return render_template(
        'admin/announcements.html',
        announcements=announcements
    )


@app.route('/admin/announcements/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_announcement_add():
    form = AnnouncementForm()

    if form.validate_on_submit():
        ann = Announcement(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id,
            target_role=form.target_role.data,
            is_pinned=form.is_pinned.data
        )

        db.session.add(ann)
        db.session.commit()

        flash('تم نشر الإعلان بنجاح', 'success')
        return redirect(url_for('admin_announcements'))

    return render_template(
        'admin/announcement_form.html',
        form=form,
        title='إضافة إعلان جديد'
    )


@app.route('/admin/announcements/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_announcement_edit(id):
    ann = Announcement.query.get_or_404(id)
    form = AnnouncementForm(obj=ann)

    if form.validate_on_submit():
        ann.title = form.title.data
        ann.content = form.content.data
        ann.target_role = form.target_role.data
        ann.is_pinned = form.is_pinned.data
        ann.updated_at = datetime.utcnow()

        db.session.commit()

        flash('تم تحديث الإعلان بنجاح', 'success')
        return redirect(url_for('admin_announcements'))

    return render_template(
        'admin/announcement_form.html',
        form=form,
        ann=ann,
        title='تعديل الإعلان'
    )


@app.route('/admin/announcements/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_announcement_delete(id):
    ann = Announcement.query.get_or_404(id)

    db.session.delete(ann)
    db.session.commit()

    flash('تم حذف الإعلان بنجاح', 'success')
    return redirect(url_for('admin_announcements'))


# ─── Admin Reports ────────────────────────────────────────────────────────────

@app.route('/admin/reports')
@login_required
@admin_required
def admin_reports():
    stats = {
        'students': Student.query.filter_by(is_active=True).count(),
        'teachers': Teacher.query.filter_by(is_active=True).count(),
        'classes': Class.query.count(),
        'subjects': Subject.query.filter_by(is_active=True).count(),
    }

    grades_by_subject = db.session.query(
        Subject.name,
        db.func.avg(Grade.score).label('avg_score'),
        db.func.count(Grade.id).label('count')
    ).join(
        Grade,
        Grade.subject_id == Subject.id
    ).group_by(Subject.id).all()

    return render_template(
        'admin/reports.html',
        stats=stats,
        grades_by_subject=grades_by_subject
    )


# ─── Admin Users CRUD ─────────────────────────────────────────────────────────

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_user_add():
    form = UserForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('اسم المستخدم مستخدم بالفعل', 'danger')
            return render_template(
                'admin/user_form.html',
                form=form,
                title='إضافة مستخدم جديد'
            )

        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            is_active=form.is_active.data
        )

        if form.password.data:
            user.set_password(form.password.data)
        else:
            user.set_password('password123')

        db.session.add(user)
        db.session.commit()

        flash('تم إضافة المستخدم بنجاح', 'success')
        return redirect(url_for('admin_users'))

    form.is_active.data = True

    return render_template(
        'admin/user_form.html',
        form=form,
        title='إضافة مستخدم جديد'
    )


@app.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_user_edit(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.is_active = form.is_active.data

        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()

        flash('تم تحديث المستخدم بنجاح', 'success')
        return redirect(url_for('admin_users'))

    return render_template(
        'admin/user_form.html',
        form=form,
        user=user,
        title='تعديل المستخدم'
    )


@app.route('/admin/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_user_delete(id):
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص', 'danger')
        return redirect(url_for('admin_users'))

    db.session.delete(user)
    db.session.commit()

    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('admin_users'))


# ─── Init DB & Seed Data ──────────────────────────────────────────────────────

def create_sample_data():
    """Create sample data for demonstration"""

    # Create admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@school.edu',
            role='admin'
        )

        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()

    # Create classes
    class_names = [
        ('الصف الأول - أ', 'الصف الأول', 'أ'),
        ('الصف الثاني - أ', 'الصف الثاني', 'أ'),
        ('الصف الثالث - أ', 'الصف الثالث', 'أ'),
        ('الصف الرابع - أ', 'الصف الرابع', 'أ'),
        ('الصف الخامس - أ', 'الصف الخامس', 'أ'),
        ('الصف السادس - أ', 'الصف السادس', 'أ'),
    ]

    classes = []

    for name, level, section in class_names:
        if not Class.query.filter_by(name=name).first():
            c = Class(
                name=name,
                grade_level=level,
                section=section,
                capacity=30
            )

            db.session.add(c)
            db.session.flush()
            classes.append(c)

        else:
            classes.append(Class.query.filter_by(name=name).first())

    # Create teachers
    teachers_data = [
        ('محمد', 'الدسوقي', 'م.الدسوقي', 'الرياضيات', 'T001'),
        ('سارة', 'أحمد', 'أ.سارة أحمد', 'اللغة العربية', 'T002'),
        ('أحمد', 'خالد', 'أ.أحمد خالد', 'العلوم', 'T003'),
        ('ندى', 'علي', 'أ.ندى علي', 'اللغة الإنجليزية', 'T004'),
    ]

    teachers = []

    for fname, lname, arabic, spec, tid in teachers_data:
        uname = f'teacher_{tid.lower()}'

        if not User.query.filter_by(username=uname).first():
            u = User(
                username=uname,
                email=f'{uname}@school.edu',
                role='teacher'
            )

            u.set_password('teacher123')
            db.session.add(u)
            db.session.flush()

            t = Teacher(
                user_id=u.id,
                teacher_id=tid,
                first_name=fname,
                last_name=lname,
                arabic_name=arabic,
                specialization=spec
            )

            db.session.add(t)
            db.session.flush()
            teachers.append(t)

        else:
            u = User.query.filter_by(username=uname).first()
            t = Teacher.query.filter_by(user_id=u.id).first()

            if t:
                teachers.append(t)

    # Create subjects
    subjects_data = [
        ('الرياضيات', 'Mathematics', 'MATH101', 0),
        ('اللغة العربية', 'Arabic Language', 'ARAB101', 1),
        ('العلوم', 'Science', 'SCI101', 2),
        ('اللغة الإنجليزية', 'English Language', 'ENG101', 3),
        ('التاريخ', 'History', 'HIST101', None),
        ('التربية الإسلامية', 'Islamic Education', 'ISLM101', None),
    ]

    subjects = []

    for name, name_en, code, teacher_idx in subjects_data:
        if not Subject.query.filter_by(code=code).first():
            teacher_id = (
                teachers[teacher_idx].id
                if teacher_idx is not None and teacher_idx < len(teachers)
                else None
            )

            s = Subject(
                name=name,
                name_en=name_en,
                code=code,
                teacher_id=teacher_id
            )

            db.session.add(s)
            db.session.flush()
            subjects.append(s)

        else:
            subjects.append(Subject.query.filter_by(code=code).first())

    # Create sample students
    students_data = [
        ('أحمد', 'محمد', 'أحمد محمد العلي', 'S001', 0),
        ('فاطمة', 'علي', 'فاطمة علي الزهراء', 'S002', 0),
        ('عمر', 'خالد', 'عمر خالد السعيد', 'S003', 1),
        ('مريم', 'إبراهيم', 'مريم إبراهيم النور', 'S004', 1),
        ('يوسف', 'أحمد', 'يوسف أحمد الكريم', 'S005', 2),
    ]

    students = []

    for fname, lname, arabic, sid, class_idx in students_data:
        uname = f'student_{sid.lower()}'

        if not User.query.filter_by(username=uname).first():
            u = User(
                username=uname,
                email=f'{uname}@school.edu',
                role='student'
            )

            u.set_password('student123')
            db.session.add(u)
            db.session.flush()

            st = Student(
                user_id=u.id,
                student_id=sid,
                first_name=fname,
                last_name=lname,
                arabic_name=arabic,
                class_id=classes[class_idx].id if class_idx < len(classes) else None
            )

            db.session.add(st)
            db.session.flush()
            students.append(st)

        else:
            u = User.query.filter_by(username=uname).first()
            st = Student.query.filter_by(user_id=u.id).first()

            if st:
                students.append(st)

    # Create sample grades
    if students and subjects:
        sample_scores = [
            95, 88, 72, 65, 91,
            78, 83, 70, 55, 99,
            76, 87, 92, 61, 84
        ]

        idx = 0

        for student in students[:3]:
            for subject in subjects[:5]:
                if not Grade.query.filter_by(
                    student_id=student.id,
                    subject_id=subject.id
                ).first():

                    score = sample_scores[idx % len(sample_scores)]

                    g = Grade(
                        student_id=student.id,
                        subject_id=subject.id,
                        score=score,
                        total_score=100,
                        term='الفصل الأول'
                    )

                    db.session.add(g)
                    idx += 1

    # Create sample attendance
    from datetime import timedelta

    if students:
        today = date.today()

        for i in range(10):
            att_date = today - timedelta(days=i)

            for student in students[:3]:
                if not Attendance.query.filter_by(
                    student_id=student.id,
                    date=att_date
                ).first():

                    status = 'present' if i % 5 != 0 else 'absent'

                    att = Attendance(
                        student_id=student.id,
                        date=att_date,
                        status=status
                    )

                    db.session.add(att)

    # Create sample announcements
    ann_data = [
        (
            'بداية الفصل الدراسي الثاني',
            'يسعدنا الإعلان عن بداية الفصل الدراسي الثاني بتاريخ 15 يناير 2025',
            'all',
            True
        ),
        (
            'تقديم الاختبارات النهائية',
            'تبدأ الاختبارات النهائية للفصل الأول في 20 ديسمبر 2024',
            'student',
            False
        ),
        (
            'اجتماع أولياء الأمور',
            'يُعقد اجتماع أولياء الأمور يوم الخميس القادم في تمام الساعة 6 مساءً',
            'all',
            False
        ),
        (
            'ورشة عمل للمعلمين',
            'ستُعقد ورشة عمل تطوير مهني للمعلمين الجمعة القادمة',
            'teacher',
            False
        ),
    ]

    admin_user = User.query.filter_by(username='admin').first()

    for title, content, role, pinned in ann_data:
        if not Announcement.query.filter_by(title=title).first():
            ann = Announcement(
                title=title,
                content=content,
                target_role=role,
                is_pinned=pinned,
                author_id=admin_user.id if admin_user else None
            )

            db.session.add(ann)

    # Create sample news
    news_data = [
        (
            'المدرسة تحصل على جائزة التميز التعليمي',
            'حصلت مدرسة المستقبل الدولية على جائزة التميز التعليمي لعام 2024 تقديراً لجهودها في تطوير المناهج الدراسية.',
            'إنجازات',
            'https://images.pexels.com/photos/8926848/pexels-photo-8926848.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600'
        ),
        (
            'انطلاق المشروع العلمي السنوي',
            'انطلق المشروع العلمي السنوي للطلاب بمشاركة أكثر من 200 طالب في مختلف المجالات العلمية.',
            'أخبار المدرسة',
            'https://images.pexels.com/photos/5905502/pexels-photo-5905502.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600'
        ),
        (
            'اليوم الرياضي السنوي',
            'أُقيم اليوم الرياضي السنوي للمدرسة بمشاركة جميع الطلاب في مختلف الأنشطة الرياضية والترفيهية.',
            'فعاليات',
            'https://images.pexels.com/photos/8927012/pexels-photo-8927012.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600'
        ),
    ]

    for title, content, cat, img in news_data:
        if not News.query.filter_by(title=title).first():
            n = News(
                title=title,
                content=content,
                category=cat,
                image_url=img,
                author_id=admin_user.id if admin_user else None
            )

            db.session.add(n)

    # Create activities
    activities_data = [
        (
            'بطولة كرة القدم المدرسية',
            'بطولة كرة القدم السنوية بين فصول المدرسة',
            'رياضي',
            'https://images.pexels.com/photos/8927012/pexels-photo-8927012.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600'
        ),
        (
            'معرض العلوم',
            'معرض العلوم السنوي لعرض مشاريع الطلاب',
            'علمي',
            'https://images.pexels.com/photos/5905502/pexels-photo-5905502.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600'
        ),
        (
            'رحلة ثقافية',
            'رحلة ثقافية تعليمية للمتاحف والمعالم التاريخية',
            'ثقافي',
            'https://images.pexels.com/photos/37898351/pexels-photo-37898351.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600'
        ),
        (
            'مسابقة الخطابة',
            'مسابقة الخطابة والإلقاء لاكتشاف المواهب',
            'ثقافي',
            'https://images.pexels.com/photos/29659894/pexels-photo-29659894.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600'
        ),
        (
            'يوم البيئة',
            'فعاليات يوم البيئة والتوعية البيئية',
            'بيئي',
            'https://images.pexels.com/photos/36098184/pexels-photo-36098184.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600'
        ),
        (
            'مهرجان الفنون',
            'مهرجان الفنون والإبداع لعرض إبداعات الطلاب',
            'فني',
            'https://images.pexels.com/photos/36781049/pexels-photo-36781049.png?auto=compress&cs=tinysrgb&fit=crop&h=400&w=600'
        ),
    ]

    for title, desc, cat, img in activities_data:
        if not Activity.query.filter_by(title=title).first():
            a = Activity(
                title=title,
                description=desc,
                category=cat,
                image_url=img,
                activity_date=date.today()
            )

            db.session.add(a)

    # Create schedules
    if classes and subjects and teachers:
        schedule_data = [
            (0, '08:00', '09:00', 0, 0, 0),
            (0, '09:00', '10:00', 0, 1, 1),
            (1, '08:00', '09:00', 0, 2, 2),
            (1, '09:00', '10:00', 0, 3, 3),
            (2, '08:00', '09:00', 0, 0, 0),
            (2, '09:00', '10:00', 0, 4, 0),
            (3, '08:00', '09:00', 0, 1, 1),
            (4, '08:00', '09:00', 0, 2, 2),
        ]

        for day, start, end, class_idx, subj_idx, teach_idx in schedule_data:
            if (
                class_idx < len(classes)
                and subj_idx < len(subjects)
                and teach_idx < len(teachers)
            ):
                if not Schedule.query.filter_by(
                    class_id=classes[class_idx].id,
                    subject_id=subjects[subj_idx].id,
                    day_of_week=day
                ).first():

                    sch = Schedule(
                        class_id=classes[class_idx].id,
                        subject_id=subjects[subj_idx].id,
                        teacher_id=teachers[teach_idx].id,
                        day_of_week=day,
                        start_time=start,
                        end_time=end
                    )

                    db.session.add(sch)

    db.session.commit()


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()

        print("\n" + "=" * 50)
        print("✅ مدرسة المستقبل الدولية - نظام الإدارة")
        print("=" * 50)
        print("🌐 الرابط: http://127.0.0.1:5000")
        print("\n📋 بيانات الدخول التجريبية:")
        print("  Admin:   admin / admin123")
        print("  Teacher: teacher_t001 / teacher123")
        print("  Student: student_s001 / student123")
        print("=" * 50 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)