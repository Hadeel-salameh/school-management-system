import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'مفتاح-سري-جدا-للمدرسة-2024'
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    SQLALCHEMY_DATABASE_URI = database_url or ('sqlite:///' + os.path.join(basedir, 'instance', 'school.db'))
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # حل مشكلة انقطاع اتصال Neon والاحتفاظ باتصال حي وآمن
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    WTF_CSRF_ENABLED = True
    SCHOOL_NAME = 'مدرسة المستقبل الدولية'
    SCHOOL_MOTTO = 'تعلم اليوم ... لقيادة الغد'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
