import os
from app import create_app, db # Import factory và db instance
# Import các models cần thiết để tạo bảng (nếu chưa tạo)
# from app.models import Task # Ví dụ

# Lấy tên cấu hình từ biến môi trường hoặc dùng mặc định 'development'
config_name = os.getenv('FLASK_CONFIG') or 'development'

# Tạo Flask app instance sử dụng factory
app = create_app(config_name)

# Context processor (ví dụ: để inject biến vào mọi template)
# @app.context_processor
# def inject_global_vars():
#     return dict(app_version="1.0")

# Lệnh CLI tùy chỉnh (ví dụ)
# @app.cli.command('init-db')
# def init_db_command():
#     """Khởi tạo database."""
#     db.create_all()
#     print('Initialized the database.')

if __name__ == '__main__':
    # Chạy app với server development của Flask
    # Debug mode sẽ được lấy từ cấu hình đã load trong create_app
    app.run() # Không cần đặt debug=True ở đây