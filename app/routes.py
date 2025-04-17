from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.services import task_service  # Import service
from app.forms import TaskForm # Import form
# Import Task model nếu cần truy vấn trực tiếp, nhưng ở đây service đã xử lý
# from app.models import Task
# from app import db # Import db nếu cần commit trực tiếp, nhưng service đã xử lý

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
            # Chuyển hướng người dùng đến trang danh sách task (sẽ tạo ở phase sau)
            # Tạm thời chuyển hướng về dashboard
            return redirect(url_for('main.dashboard')) # Hoặc 'main.task_list' nếu đã có
        else:
            # Có lỗi xảy ra khi tạo task trong service
            flash('Không thể tạo tác vụ. Đã có lỗi xảy ra.', 'danger')
            # Render lại form để người dùng sửa
            return render_template('task_form.html', title='Tạo tác vụ mới', form=form)

    # Xử lý khi người dùng truy cập trang lần đầu (GET request) hoặc khi form không hợp lệ
    # Nếu là GET, form trống. Nếu là POST không hợp lệ, form chứa dữ liệu cũ và lỗi validation.
    return render_template('task_form.html', title='Tạo tác vụ mới', form=form)

# Các route khác sẽ được thêm vào đây... 