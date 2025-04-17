import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler
from config import config # Import dictionary cấu hình

# Khởi tạo các extensions (nhưng chưa gắn vào app cụ thể)
db = SQLAlchemy()
csrf = CSRFProtect()
scheduler = BackgroundScheduler(daemon=True) # Chạy nền và tự thoát khi app chính thoát

def create_app(config_name='default'):
    """Factory function để tạo và cấu hình Flask app."""
    app = Flask(__name__,
                instance_relative_config=True, # Cho phép load config từ thư mục instance
                static_folder='static', # Thư mục chứa file tĩnh (CSS, JS, images)
                template_folder='templates' # Thư mục chứa file template Jinja2
                )

    # Load cấu hình từ lớp Config tương ứng trong config.py
    # Ưu tiên FLASK_CONFIG từ biến môi trường, nếu không có thì dùng config_name (mặc định là 'default')
    app_config_name = os.getenv('FLASK_CONFIG') or config_name
    app.config.from_object(config[app_config_name])

    # Tạo thư mục instance nếu chưa tồn tại
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Khởi tạo các extensions với app
    db.init_app(app)
    csrf.init_app(app)

    # Cấu hình logging cơ bản (ghi ra console)
    # Cấu hình logging chi tiết hơn sẽ thực hiện ở Phase 7
    if not app.debug and not app.testing:
        # Chỉ cấu hình logging file khi không ở chế độ debug hoặc testing
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/web_scraper.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Web Scraping Bot startup')
    else:
        # Trong chế độ debug/testing, chỉ cần log ra console ở level DEBUG
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        app.logger.info('Web Scraping Bot startup in DEBUG/TESTING mode')


    # Khởi động APScheduler
    if app.config['SCHEDULER_API_ENABLED'] and not scheduler.running:

        try:
            scheduler.start()
            app.logger.info('APScheduler started.')
        except Exception as e:
             app.logger.error(f"Error starting APScheduler: {e}")
        # Đăng ký hàm shutdown để dừng scheduler khi app thoát
        import atexit
        atexit.register(lambda: scheduler.shutdown())



    from .routes import main as main_blueprint # Import Blueprint 'main'
    app.register_blueprint(main_blueprint) # Đăng ký Blueprint với app

    # Import models để SQLAlchemy biết về chúng (quan trọng cho db.create_all())
    from . import models

    return app