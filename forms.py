from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField, BooleanField,
                     TextAreaField, IntegerField, FloatField, DateField,
                     SubmitField, HiddenField)
from wtforms.validators import (DataRequired, Length, Email, Optional,
                                 NumberRange, EqualTo, ValidationError)


class LoginForm(FlaskForm):
    role = SelectField('نوع المستخدم', choices=[
        ('student', 'طالب'),
        ('teacher', 'معلم'),
        ('admin', 'مدير')
    ], validators=[DataRequired(message='الرجاء اختيار نوع المستخدم')])
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='الرجاء إدخال اسم المستخدم'),
        Length(min=3, max=64, message='اسم المستخدم يجب أن يكون بين 3 و 64 حرفاً')
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='الرجاء إدخال كلمة المرور'),
        Length(min=4, max=128, message='كلمة المرور يجب أن تكون على الأقل 4 أحرف')
    ])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')


class StudentForm(FlaskForm):
    first_name = StringField('الاسم الأول', validators=[
        DataRequired(message='الاسم الأول مطلوب'),
        Length(max=50)
    ])
    last_name = StringField('اسم العائلة', validators=[
        DataRequired(message='اسم العائلة مطلوب'),
        Length(max=50)
    ])
    arabic_name = StringField('الاسم الكامل بالعربية', validators=[Optional(), Length(max=100)])
    student_id = StringField('الرقم الطلابي', validators=[
        DataRequired(message='الرقم الطلابي مطلوب'),
        Length(max=20)
    ])
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='اسم المستخدم مطلوب'),
        Length(min=3, max=64)
    ])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email(message='بريد إلكتروني غير صالح')])
    password = PasswordField('كلمة المرور', validators=[Optional(), Length(min=4)])
    date_of_birth = DateField('تاريخ الميلاد', validators=[Optional()])
    gender = SelectField('الجنس', choices=[
        ('', 'اختر الجنس'),
        ('male', 'ذكر'),
        ('female', 'أنثى')
    ], validators=[Optional()])
    phone = StringField('رقم الهاتف', validators=[Optional(), Length(max=20)])
    address = TextAreaField('العنوان', validators=[Optional()])
    parent_name = StringField('اسم ولي الأمر', validators=[Optional(), Length(max=100)])
    parent_phone = StringField('هاتف ولي الأمر', validators=[Optional(), Length(max=20)])
    class_id = SelectField('الصف', coerce=int, validators=[Optional()])
    enrollment_date = DateField('تاريخ التسجيل', validators=[Optional()])
    submit = SubmitField('حفظ')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_id.choices = [(0, 'اختر الصف')]


class TeacherForm(FlaskForm):
    first_name = StringField('الاسم الأول', validators=[
        DataRequired(message='الاسم الأول مطلوب'),
        Length(max=50)
    ])
    last_name = StringField('اسم العائلة', validators=[
        DataRequired(message='اسم العائلة مطلوب'),
        Length(max=50)
    ])
    arabic_name = StringField('الاسم الكامل بالعربية', validators=[Optional(), Length(max=100)])
    teacher_id = StringField('رقم المعلم', validators=[
        DataRequired(message='رقم المعلم مطلوب'),
        Length(max=20)
    ])
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='اسم المستخدم مطلوب'),
        Length(min=3, max=64)
    ])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email(message='بريد إلكتروني غير صالح')])
    password = PasswordField('كلمة المرور', validators=[Optional(), Length(min=4)])
    specialization = StringField('التخصص', validators=[Optional(), Length(max=100)])
    phone = StringField('رقم الهاتف', validators=[Optional(), Length(max=20)])
    address = TextAreaField('العنوان', validators=[Optional()])
    hire_date = DateField('تاريخ التعيين', validators=[Optional()])
    qualification = StringField('المؤهل العلمي', validators=[Optional(), Length(max=200)])
    bio = TextAreaField('نبذة شخصية', validators=[Optional()])
    submit = SubmitField('حفظ')


class ClassForm(FlaskForm):
    name = StringField('اسم الصف', validators=[
        DataRequired(message='اسم الصف مطلوب'),
        Length(max=100)
    ])
    grade_level = StringField('المرحلة الدراسية', validators=[
        DataRequired(message='المرحلة مطلوبة'),
        Length(max=50)
    ])
    section = StringField('الشعبة', validators=[Optional(), Length(max=10)])
    academic_year = StringField('العام الدراسي', validators=[Optional(), Length(max=20)])
    capacity = IntegerField('السعة الاستيعابية', validators=[Optional(), NumberRange(min=1, max=100)])
    description = TextAreaField('وصف', validators=[Optional()])
    submit = SubmitField('حفظ')


class SubjectForm(FlaskForm):
    name = StringField('اسم المادة', validators=[
        DataRequired(message='اسم المادة مطلوب'),
        Length(max=100)
    ])
    name_en = StringField('الاسم بالإنجليزية', validators=[Optional(), Length(max=100)])
    code = StringField('كود المادة', validators=[
        DataRequired(message='كود المادة مطلوب'),
        Length(max=20)
    ])
    teacher_id = SelectField('المعلم المسؤول', coerce=int, validators=[Optional()])
    total_marks = IntegerField('الدرجة الكلية', validators=[Optional(), NumberRange(min=1)])
    passing_marks = IntegerField('درجة النجاح', validators=[Optional(), NumberRange(min=1)])
    description = TextAreaField('وصف', validators=[Optional()])
    submit = SubmitField('حفظ')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_id.choices = [(0, 'بدون معلم')]


class GradeForm(FlaskForm):
    student_id = SelectField('الطالب', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('المادة', coerce=int, validators=[DataRequired()])
    score = FloatField('الدرجة', validators=[DataRequired(message='الدرجة مطلوبة'), NumberRange(min=0)])
    total_score = FloatField('الدرجة الكلية', validators=[Optional(), NumberRange(min=1)])
    exam_type = SelectField('نوع الاختبار', choices=[
        ('نهائي', 'نهائي'),
        ('منتصف الفصل', 'منتصف الفصل'),
        ('أسبوعي', 'أسبوعي'),
        ('شفهي', 'شفهي'),
        ('عملي', 'عملي')
    ])
    term = SelectField('الفصل الدراسي', choices=[
        ('الفصل الأول', 'الفصل الأول'),
        ('الفصل الثاني', 'الفصل الثاني'),
        ('الفصل الثالث', 'الفصل الثالث')
    ])
    academic_year = StringField('العام الدراسي', validators=[Optional()])
    remarks = TextAreaField('ملاحظات', validators=[Optional()])
    submit = SubmitField('حفظ')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_id.choices = [(0, 'اختر الطالب')]
        self.subject_id.choices = [(0, 'اختر المادة')]


class AttendanceForm(FlaskForm):
    student_id = SelectField('الطالب', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('المادة', coerce=int, validators=[Optional()])
    date = DateField('التاريخ', validators=[DataRequired(message='التاريخ مطلوب')])
    status = SelectField('الحالة', choices=[
        ('present', 'حاضر'),
        ('absent', 'غائب'),
        ('late', 'متأخر'),
        ('excused', 'غياب بعذر')
    ], validators=[DataRequired()])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    submit = SubmitField('حفظ')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_id.choices = [(0, 'اختر الطالب')]
        self.subject_id.choices = [(0, 'اختر المادة')]


class AnnouncementForm(FlaskForm):
    title = StringField('عنوان الإعلان', validators=[
        DataRequired(message='العنوان مطلوب'),
        Length(max=200)
    ])
    content = TextAreaField('المحتوى', validators=[
        DataRequired(message='المحتوى مطلوب')
    ])
    target_role = SelectField('الجمهور المستهدف', choices=[
        ('all', 'الجميع'),
        ('student', 'الطلاب'),
        ('teacher', 'المعلمون'),
        ('admin', 'الإدارة')
    ])
    is_pinned = BooleanField('تثبيت الإعلان')
    submit = SubmitField('نشر الإعلان')


class ExamForm(FlaskForm):
    title = StringField('عنوان الاختبار', validators=[
        DataRequired(message='العنوان مطلوب'),
        Length(max=200)
    ])
    subject_id = SelectField('المادة', coerce=int, validators=[DataRequired()])
    class_id = SelectField('الصف', coerce=int, validators=[Optional()])
    exam_date = DateField('تاريخ الاختبار', validators=[Optional()])
    start_time = StringField('وقت البدء', validators=[Optional()])
    duration = IntegerField('المدة (بالدقائق)', validators=[Optional(), NumberRange(min=1)])
    total_marks = IntegerField('الدرجة الكلية', validators=[Optional(), NumberRange(min=1)])
    exam_type = SelectField('نوع الاختبار', choices=[
        ('نهائي', 'نهائي'),
        ('منتصف الفصل', 'منتصف الفصل'),
        ('أسبوعي', 'أسبوعي'),
        ('مختبري', 'مختبري')
    ])
    location = StringField('القاعة/الغرفة', validators=[Optional(), Length(max=100)])
    description = TextAreaField('وصف', validators=[Optional()])
    submit = SubmitField('حفظ')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject_id.choices = [(0, 'اختر المادة')]
        self.class_id.choices = [(0, 'جميع الصفوف')]


class AssignmentForm(FlaskForm):
    title = StringField('عنوان الواجب', validators=[
        DataRequired(message='العنوان مطلوب'),
        Length(max=200)
    ])
    description = TextAreaField('الوصف والتعليمات', validators=[Optional()])
    subject_id = SelectField('المادة', coerce=int, validators=[DataRequired()])
    class_id = SelectField('الصف', coerce=int, validators=[Optional()])
    due_date = DateField('تاريخ التسليم', validators=[Optional()])
    total_marks = IntegerField('الدرجة الكلية', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('حفظ')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject_id.choices = [(0, 'اختر المادة')]
        self.class_id.choices = [(0, 'جميع الصفوف')]


class UserForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='اسم المستخدم مطلوب'),
        Length(min=3, max=64)
    ])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email()])
    password = PasswordField('كلمة المرور', validators=[Optional(), Length(min=4)])
    role = SelectField('الدور', choices=[
        ('student', 'طالب'),
        ('teacher', 'معلم'),
        ('admin', 'مدير')
    ])
    is_active = BooleanField('نشط')
    submit = SubmitField('حفظ')


class ContactForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[
        DataRequired(message='الاسم الكامل مطلوب'),
        Length(max=100)
    ])
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message='البريد الإلكتروني مطلوب'),
        Email(message='بريد إلكتروني غير صالح')
    ])
    subject = StringField('الموضوع', validators=[
        DataRequired(message='الموضوع مطلوب'),
        Length(max=200)
    ])
    message = TextAreaField('الرسالة', validators=[
        DataRequired(message='الرسالة مطلوبة')
    ])
    submit = SubmitField('إرسال الرسالة')
