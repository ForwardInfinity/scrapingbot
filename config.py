import os
from dotenv import load_dotenv

# Xác định đường dẫn tuyệt đối của thư mục gốc dự án
basedir = os.path.abspath(os.path.dirname(__file__))
# Load các biến môi trường từ file .env
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Lớp cấu hình cơ sở."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # Cần thiết cho session, flash, CSRF
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Tắt cảnh báo không cần thiết

    # Cấu hình APScheduler (ví dụ)
    SCHEDULER_API_ENABLED = True

    # Các cấu hình khác có thể thêm vào đây
    # ví dụ: MAIL_SERVER, MAIL_PORT, ...

class DevelopmentConfig(Config):
    """Cấu hình cho môi trường development."""
    DEBUG = True
    # Có thể ghi đè hoặc thêm cấu hình riêng cho dev
    # SQLALCHEMY_ECHO = True # Bật log câu lệnh SQL

class TestingConfig(Config):
    """Cấu hình cho môi trường testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Sử dụng DB trong bộ nhớ cho test
    WTF_CSRF_ENABLED = False # Tắt CSRF token trong test form
    # SCHEDULER_API_ENABLED = False # Có thể tắt scheduler khi test

class ProductionConfig(Config):
    """Cấu hình cho môi trường production."""
    DEBUG = False
    TESTING = False
    # Cần đảm bảo các cấu hình bảo mật và hiệu năng cho production
    # ví dụ: sử dụng database khác, cấu hình logging chi tiết hơn

# Dictionary để dễ dàng truy cập các lớp cấu hình theo tên môi trường
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig # Mặc định nếu FLASK_ENV không được đặt
}