from datetime import datetime, timezone
from app import db # Giả sử db đã được khởi tạo trong app/__init__.py

class Task(db.Model):
    """Định nghĩa model cho bảng Task trong cơ sở dữ liệu."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    selectors = db.Column(db.Text, nullable=False)  # Lưu dưới dạng JSON string
    schedule = db.Column(db.String(128), nullable=True) # Lưu thông tin lịch trình (ví dụ: cron expression hoặc mô tả)
    status = db.Column(db.String(64), nullable=False, default='Pending') # Pending, Running, Completed, Failed, Scheduled
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_run = db.Column(db.DateTime, nullable=True)
    result = db.Column(db.Text, nullable=True)      # Lưu kết quả scrape dưới dạng JSON string
    error_message = db.Column(db.Text, nullable=True) # Lưu thông báo lỗi nếu có

    def __repr__(self):
        return f'<Task {self.name}>' 