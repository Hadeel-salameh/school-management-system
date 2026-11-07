# مدرسة المستقبل الدولية - نظام إدارة المدرسة

نظام إدارة مدرسة متكامل مبني باستخدام Flask Framework

## المتطلبات

- Python 3.8+
- pip

## التثبيت والتشغيل

### 1. تثبيت المتطلبات

```bash
cd school_management
pip install -r requirements.txt
```

### 2. تشغيل التطبيق

```bash
python app.py
```

### 3. فتح المتصفح

```
http://127.0.0.1:5000
```

## بيانات الدخول التجريبية

| الدور | اسم المستخدم | كلمة المرور |
|-------|-------------|------------|
| مدير النظام | admin | admin123 |
| معلم | teacher_t001 | teacher123 |
| طالب | student_s001 | student123 |

## هيكل المشروع

```
school_management/
├── app.py              # التطبيق الرئيسي
├── forms.py            # نماذج Flask-WTF
├── models.py           # نماذج قاعدة البيانات
├── config.py           # الإعدادات
├── requirements.txt    # المتطلبات
│
├── templates/
│   ├── layout.html          # Template الرئيسي
│   ├── dashboard_layout.html # Template لوحات التحكم
│   ├── index.html           # الصفحة الرئيسية
│   ├── about.html           # من نحن
│   ├── teachers.html        # الكادر التعليمي
│   ├── news.html            # الأخبار
│   ├── activities.html      # الأنشطة
│   ├── contact.html         # تواصل معنا
│   ├── login.html           # تسجيل الدخول
│   │
│   ├── student/             # صفحات الطالب
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   ├── grades.html
│   │   ├── attendance.html
│   │   ├── schedule.html
│   │   ├── assignments.html
│   │   └── reports.html
│   │
│   ├── teacher/             # صفحات المعلم
│   │   ├── dashboard.html
│   │   ├── students.html
│   │   ├── grades.html
│   │   ├── attendance.html
│   │   ├── assignments.html
│   │   └── exams.html
│   │
│   └── admin/               # صفحات الإدارة
│       ├── dashboard.html
│       ├── students.html
│       ├── student_form.html
│       ├── teachers.html
│       ├── teacher_form.html
│       ├── classes.html
│       ├── class_form.html
│       ├── subjects.html
│       ├── subject_form.html
│       ├── grades.html
│       ├── grade_form.html
│       ├── attendance.html
│       ├── attendance_form.html
│       ├── exams.html
│       ├── exam_form.html
│       ├── announcements.html
│       ├── announcement_form.html
│       ├── reports.html
│       └── users.html
│
├── static/
│   ├── css/style.css        # الأنماط الرئيسية
│   └── js/script.js         # JavaScript الرئيسي
│
└── instance/
    └── school.db            # قاعدة البيانات SQLite
```

## الميزات

### صفحات عامة
- ✅ الصفحة الرئيسية مع Hero Section
- ✅ صفحة من نحن
- ✅ صفحة الكادر التعليمي
- ✅ صفحة الأخبار مع فلتر الفئات
- ✅ صفحة الأنشطة مع فلتر
- ✅ صفحة تواصل معنا

### نظام المصادقة
- ✅ تسجيل دخول متعدد الأدوار
- ✅ حماية المسارات حسب الدور
- ✅ تسجيل الخروج
- ✅ Remember Me

### لوحة الطالب
- ✅ Dashboard مع الإحصائيات
- ✅ الملف الشخصي
- ✅ عرض الدرجات مع رسم بياني
- ✅ سجل الحضور والغياب
- ✅ الجدول الدراسي
- ✅ الواجبات
- ✅ التقارير

### لوحة المعلم
- ✅ Dashboard مع الإحصائيات
- ✅ قائمة الطلاب
- ✅ رصد الدرجات
- ✅ تسجيل الحضور
- ✅ إدارة الواجبات
- ✅ إدارة الاختبارات

### لوحة الإدارة (CRUD كامل)
- ✅ Dashboard مع Charts
- ✅ إدارة الطلاب (CRUD + بحث + pagination)
- ✅ إدارة المعلمين (CRUD)
- ✅ إدارة الصفوف (CRUD)
- ✅ إدارة المواد الدراسية (CRUD)
- ✅ إدارة الدرجات (CRUD + pagination)
- ✅ إدارة الحضور والغياب (CRUD + pagination)
- ✅ إدارة الاختبارات (CRUD)
- ✅ إدارة الإعلانات (CRUD)
- ✅ إدارة المستخدمين (CRUD)
- ✅ التقارير والإحصائيات مع Charts

## التقنيات المستخدمة

- **Backend**: Python, Flask, Flask-WTF, Flask-Login, Flask-SQLAlchemy
- **Database**: SQLite (قابل للتغيير)
- **Frontend**: Bootstrap 5 RTL, Bootstrap Icons, Chart.js
- **Typography**: Google Fonts (Cairo, Tajawal)
- **Language**: Arabic (RTL)
