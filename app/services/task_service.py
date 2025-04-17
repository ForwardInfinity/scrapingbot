import json
from flask import current_app
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

def get_tasks(page, per_page, search_term=None):
    """Lấy danh sách các task, hỗ trợ tìm kiếm và phân trang.

    Args:
        page (int): Số trang hiện tại.
        per_page (int): Số lượng task trên mỗi trang.
        search_term (str, optional): Từ khóa tìm kiếm theo tên task. Mặc định là None.

    Returns:
        Pagination: Đối tượng Pagination của Flask-SQLAlchemy chứa các task
                    cho trang hiện tại và thông tin phân trang.
    """
    query = Task.query.order_by(Task.created_at.desc())

    if search_term:
        # Sử dụng ilike để tìm kiếm không phân biệt hoa thường
        query = query.filter(Task.name.ilike(f'%{search_term}%'))

    # Thực hiện phân trang
    # paginate trả về một đối tượng Pagination
    # tham số error_out=False để không raise 404 nếu page không hợp lệ,
    # thay vào đó trả về trang đầu tiên hoặc trang cuối cùng.
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return pagination

# === Hàm lấy Task theo ID ===
def get_task_by_id(task_id):
    """Lấy một task cụ thể từ database bằng ID.

    Args:
        task_id (int): ID của task cần lấy.

    Returns:
        Task: Đối tượng Task tương ứng với ID, hoặc None nếu không tìm thấy.
    """
    # Sử dụng db.session.get theo SQLAlchemy 2.x
    return db.session.get(Task, task_id)

# === Hàm cập nhật Task ===
def update_task(task_id, form_data):
    """Cập nhật thông tin cho một task đã có.

    Args:
        task_id (int): ID của task cần cập nhật.
        form_data (dict): Dữ liệu đã được validate từ TaskForm.

    Returns:
        Task: Đối tượng Task đã được cập nhật, hoặc None nếu có lỗi hoặc không tìm thấy task.
    """
    task = get_task_by_id(task_id)
    if not task:
        return None

    try:
        # Cập nhật các trường từ form_data
        task.name = form_data['name']
        task.url = form_data['url']

        # Xử lý selectors tương tự như create_task
        selectors_list = form_data.get('selectors', [])
        task.selectors = json.dumps(selectors_list)

        # Xử lý schedule tương tự như create_task
        schedule_type = form_data.get('schedule_type')
        schedule_value = form_data.get('schedule_value')
        if schedule_type and schedule_type != 'none' and schedule_value:
            task.schedule = f"{schedule_type}:{schedule_value}"
        else:
            task.schedule = None # Nếu chọn 'Không lập lịch'

        # Lưu ý: Không cập nhật status, last_run, result, error_message ở đây
        # Các trường này sẽ được cập nhật bởi quá trình chạy task

        db.session.commit() # Commit thay đổi
        return task
    except Exception as e:
        # Log lỗi khi cập nhật task
        current_app.logger.error(f"Error updating task {task_id}: {e}")
        db.session.rollback()
        return None

# === Hàm xóa Task ===
def delete_task(task_id):
    """Xóa một task khỏi cơ sở dữ liệu.

    Args:
        task_id (int): ID của task cần xóa.

    Returns:
        bool: True nếu xóa thành công, False nếu không tìm thấy task hoặc có lỗi.
    """
    task = get_task_by_id(task_id)
    if not task:
        return False

    try:
        db.session.delete(task)
        db.session.commit()
        return True
    except Exception as e:
        # Log lỗi khi xóa task
        current_app.logger.error(f"Error deleting task {task_id}: {e}")
        db.session.rollback()
        return False