from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, abort
from app.services import task_service  # Import service
from app.forms import TaskForm, DeleteForm # Import form, Thêm DeleteForm
# Import Task model nếu cần truy vấn trực tiếp, nhưng ở đây service đã xử lý
from app.models import Task
# from app import db # Import db nếu cần commit trực tiếp, nhưng service đã xử lý
import json # Cần import json để parse selectors khi edit

main = Blueprint('main', __name__)

@main.route('/')
def dashboard():
    """Route hiển thị trang Dashboard chính."""
    stats = task_service.get_dashboard_stats() # Gọi service để lấy dữ liệu
    # Render template dashboard.html và truyền dữ liệu stats vào
    return render_template('dashboard.html', title='Dashboard', stats=stats)

# === Route cho việc tạo Task mới ===
@main.route('/tasks/new', methods=['GET', 'POST'])
def new_task():
    """Route để hiển thị form và xử lý tạo Task mới."""
    # Khởi tạo TaskForm
    form = TaskForm()

    # Xử lý khi người dùng submit form (POST request)
    if form.validate_on_submit():
        # Dữ liệu form hợp lệ
        # Gọi service create_task với dữ liệu từ form
        task = task_service.create_task(form.data)
        if task:
            # Tạo task thành công
            flash(f'Đã tạo tác vụ "{task.name}" thành công!', 'success')
            # Chuyển hướng người dùng đến trang danh sách task theo yêu cầu
            return redirect(url_for('main.task_list'))
        else:
            # Có lỗi xảy ra khi tạo task trong service
            flash('Không thể tạo tác vụ. Đã có lỗi xảy ra.', 'danger')
            # Render lại form để người dùng sửa
            return render_template('task_form.html', title='Tạo tác vụ mới', form=form)

    # Xử lý khi người dùng truy cập trang lần đầu (GET request) hoặc khi form không hợp lệ
    # Nếu là GET, form trống. Nếu là POST không hợp lệ, form chứa dữ liệu cũ và lỗi validation.
    return render_template('task_form.html', title='Tạo tác vụ mới', form=form)

# === Route cho việc xem danh sách Tasks ===
@main.route('/tasks')
def task_list():
    """Route hiển thị danh sách các Task với phân trang và tìm kiếm."""
    # Lấy tham số 'page' từ query string, mặc định là 1, kiểu integer
    page = request.args.get('page', 1, type=int)
    # Lấy tham số 'search' từ query string, mặc định là chuỗi rỗng
    search_term = request.args.get('search', '')

    # Lấy cấu hình số task trên mỗi trang từ app config
    # Cần import current_app từ flask
    from flask import current_app
    per_page = current_app.config.get('TASKS_PER_PAGE', 10) # 10 là giá trị mặc định phòng trường hợp chưa config

    # Gọi service để lấy đối tượng Pagination
    pagination = task_service.get_tasks(page=page, per_page=per_page, search_term=search_term if search_term else None)

    # Tạo instance của DeleteForm để truyền vào template (cho CSRF)
    delete_form = DeleteForm()

    # Render template danh sách task, truyền đối tượng pagination, search_term và delete_form
    return render_template('task_list.html',
                           title='Danh sách Tác vụ',
                           pagination=pagination,
                           search_term=search_term,
                           delete_form=delete_form) # Truyền delete_form vào context

# === Route cho việc sửa Task ===
@main.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    """Route để hiển thị form và xử lý cập nhật Task."""
    # Lấy task hiện tại từ service
    task = task_service.get_task_by_id(task_id)
    # Nếu không tìm thấy task, trả về lỗi 404
    if not task:
        abort(404)

    # Khởi tạo TaskForm
    form = TaskForm(obj=task) # Truyền obj=task để điền dữ liệu ban đầu

    # Xử lý khi người dùng submit form (POST request)
    if form.validate_on_submit():
        # Dữ liệu form hợp lệ
        updated_task = task_service.update_task(task_id, form.data)
        if updated_task:
            flash(f'Đã cập nhật tác vụ "{updated_task.name}" thành công!', 'success')
            return redirect(url_for('main.task_list'))
        else:
            flash('Không thể cập nhật tác vụ. Đã có lỗi xảy ra.', 'danger')
            # Render lại form, không cần điền lại vì form đã giữ giá trị submit
            return render_template('task_form.html', title='Sửa Tác vụ', form=form, task_id=task_id)

    # Xử lý khi người dùng truy cập trang lần đầu (GET request)
    # hoặc khi form POST không hợp lệ
    elif request.method == 'GET':
        # Điền dữ liệu selectors từ JSON vào form
        try:
            selectors_data = json.loads(task.selectors)
            # Xóa các entry mặc định nếu có và điền dữ liệu thực tế
            while len(form.selectors.entries) > 0:
                form.selectors.pop_entry()
            for item in selectors_data:
                form.selectors.append_entry(item)
            # Nếu sau khi load, không có selector nào, thêm một entry rỗng để UX tốt hơn
            if not form.selectors.entries:
                 form.selectors.append_entry({}) # Thêm entry rỗng
        except (json.JSONDecodeError, TypeError): # Bắt cả TypeError nếu task.selectors là None
            flash('Lỗi khi đọc dữ liệu selectors hiện tại hoặc không có selectors.', 'warning')
            # Để selectors trống nếu không parse được, nhưng vẫn thêm 1 entry rỗng
            if not form.selectors.entries:
                 form.selectors.append_entry({}) # Thêm entry rỗng

        # Điền dữ liệu schedule từ chuỗi đã lưu
        if task.schedule and ':' in task.schedule:
            schedule_parts = task.schedule.split(':', 1)
            form.schedule_type.data = schedule_parts[0]
            form.schedule_value.data = schedule_parts[1]
        else:
            form.schedule_type.data = 'none'

    # Render template với dữ liệu đã điền (GET) hoặc lỗi validation (POST)
    return render_template('task_form.html', title='Sửa Tác vụ', form=form, task_id=task_id)

# === Route cho việc xóa Task ===
@main.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task_route(task_id):
    """Route để xử lý yêu cầu xóa Task (chỉ chấp nhận POST)."""
    # Lấy tên task trước khi xóa để hiển thị thông báo
    task = task_service.get_task_by_id(task_id)
    if not task:
        abort(404)
    task_name = task.name

    # Gọi service để xóa task
    deleted = task_service.delete_task(task_id)

    if deleted:
        flash(f'Đã xóa tác vụ "{task_name}" thành công!', 'success')
    else:
        flash(f'Không thể xóa tác vụ "{task_name}". Đã có lỗi xảy ra.', 'danger')

    # Chuyển hướng về trang danh sách task
    return redirect(url_for('main.task_list'))

# Các route khác sẽ được thêm vào đây...