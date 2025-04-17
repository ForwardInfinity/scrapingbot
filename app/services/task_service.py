import json
from app import db
from app.models import Task

def get_dashboard_stats():
    """Lấy dữ liệu thống kê giả lập cho trang Dashboard."""

    return {
        'total_tasks': 5,          # Giả lập có 5 task
        'completed_tasks': 2,   # Giả lập có 2 task hoàn thành
        'running_tasks': 1,     # Giả lập có 1 task đang chạy
        'failed_tasks': 0,        # Giả lập không có task lỗi
        'scheduled_tasks': 1      # Giả lập có 1 task được lập lịch
    }

def create_task(form_data):
    """Tạo một task scraping mới và lưu vào cơ sở dữ liệu.

    Args:
        form_data (dict): Dữ liệu đã được validate từ TaskForm.

    Returns:
        Task: Đối tượng Task vừa được tạo và lưu, hoặc None nếu có lỗi.
    """
    try:
        # Dữ liệu selectors từ form là list các dictionary
        selectors_list = form_data.get('selectors', [])
        # Chuyển đổi list selectors thành chuỗi JSON để lưu vào DB
        selectors_json = json.dumps(selectors_list)

        # Lấy giá trị lập lịch, nếu không có thì là None
        schedule_type = form_data.get('schedule_type')
        schedule_value = form_data.get('schedule_value')
        schedule_info = None
        if schedule_type and schedule_type != 'none' and schedule_value:
            # Lưu cả type và value, ví dụ: "interval:3600" hoặc "cron:0 * * * *"
            # Hoặc bạn có thể lưu vào 2 cột riêng nếu muốn truy vấn phức tạp hơn
            schedule_info = f"{schedule_type}:{schedule_value}"

        # Tạo đối tượng Task mới
        new_task = Task(
            name=form_data['name'],
            url=form_data['url'],
            selectors=selectors_json,
            schedule=schedule_info,
            # status mặc định là 'Pending' theo model
        )

        # Thêm vào session và commit vào DB
        db.session.add(new_task)
        db.session.commit()
        return new_task
    except Exception as e:
        # Log lỗi ở đây nếu cần
        # current_app.logger.error(f"Error creating task: {e}")
        db.session.rollback() # Rollback nếu có lỗi xảy ra
        return None 