from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, abort, Response, make_response, jsonify
from app.services import task_service, scraping_service # Import thêm scraping_service
from app.forms import TaskForm, DeleteForm # Import form, Thêm DeleteForm
# Import Task model nếu cần truy vấn trực tiếp, nhưng ở đây service đã xử lý
from app.models import Task
from app import db, scheduler, csrf # Import db, scheduler và csrf từ app factory
import json # Cần import json để parse selectors khi edit
import logging # Import logging
# Thêm import cần thiết cho route xem kết quả và download CSV
from sqlalchemy.orm.exc import NoResultFound
import csv
import io
# Thêm import cho chatbot
from app.chatbot_logic import get_bot_response

logger = logging.getLogger(__name__) # Khởi tạo logger

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

# === Route để kích hoạt chạy Task thủ công ===
@main.route('/tasks/<int:task_id>/run', methods=['POST'])
def run_task_route(task_id):
    """Kích hoạt chạy tác vụ scraping thủ công bằng cách thêm job vào APScheduler."""
    task = db.session.get(Task, task_id)
    if not task:
        flash(f'Không tìm thấy tác vụ với ID {task_id}.', 'danger')
        return redirect(url_for('main.task_list'))

    try:
        # Kiểm tra xem scheduler có đang chạy không
        if not scheduler.running:
            logger.error("APScheduler is not running. Cannot schedule job.")
            flash('Bộ lập lịch đang không hoạt động, không thể yêu cầu chạy tác vụ.', 'danger')
            return redirect(url_for('main.task_list'))

        # Thêm job chạy ngay lập tức (run_date=None tương đương với chạy ngay)
        # ID của job nên là duy nhất, ví dụ: f'manual_run_{task.id}_{datetime.now().timestamp()}'
        # để tránh trùng lặp nếu người dùng nhấn nút nhiều lần nhanh chóng
        # Tuy nhiên, để đơn giản và khớp với việc lập lịch sau này, có thể dùng f'task_{task.id}'
        # và dùng replace_existing=True, nhưng cần kiểm tra xem có job định kỳ nào đang chạy không
        # -> Giải pháp an toàn hơn là dùng ID job riêng cho chạy thủ công
        # Hoặc đơn giản hơn là không đặt ID, để APScheduler tự tạo ID.
        # Ở đây, ta sẽ sử dụng phương án đơn giản nhất: không đặt ID cụ thể cho job chạy một lần.

        scheduler.add_job(
            func=scraping_service.run_scraping_task,
            args=[task_id],
            trigger='date', # Chạy một lần vào thời điểm được thêm
            # id=f'manual_run_{task.id}', # Có thể bỏ id để tự sinh
            # replace_existing=True # Có thể cần nếu dùng id cố định
            misfire_grace_time=60 # Cho phép trễ 60s nếu scheduler bị tắc nghẽn
        )
        # Cập nhật trạng thái thành Pending để người dùng biết là đã đưa vào hàng đợi
        # (Mặc dù job 'date' thường chạy ngay, nhưng để nhất quán với logic scheduler)
        task.status = 'Pending'
        db.session.commit()

        logger.info(f"Đã thêm job chạy thủ công cho task ID: {task_id}")
        flash(f'Đã yêu cầu chạy tác vụ "{task.name}". Trạng thái sẽ sớm được cập nhật.', 'info')

    except Exception as e:
        db.session.rollback() # Rollback nếu có lỗi khi commit status hoặc thêm job
        logger.error(f"Lỗi khi thêm job chạy thủ công cho task ID: {task_id}. Lỗi: {e}", exc_info=True)
        flash(f'Đã xảy ra lỗi khi yêu cầu chạy tác vụ: {e}', 'danger')

    return redirect(url_for('main.task_list'))

# === Route để xem kết quả Task ===
@main.route('/tasks/<int:task_id>/results')
def view_results(task_id):
    """Route để hiển thị kết quả của một Task đã hoàn thành."""
    try:
        # Lấy task từ DB, hoặc trả 404 nếu không tồn tại
        task = db.session.get(Task, task_id)
        if not task:
            logger.warning(f"Truy cập xem kết quả cho task ID không tồn tại: {task_id}")
            abort(404) # Không tìm thấy task

        # Kiểm tra trạng thái và kết quả
        if task.status != 'Completed':
            logger.info(f"Task ID {task_id} chưa hoàn thành (trạng thái: {task.status}). Không thể xem kết quả.")
            flash('Tác vụ chưa hoàn thành hoặc đã thất bại. Không có kết quả để hiển thị.', 'warning')
            return redirect(url_for('main.task_list'))

        if not task.result:
            logger.info(f"Task ID {task_id} đã hoàn thành nhưng không có dữ liệu kết quả.")
            flash('Tác vụ đã hoàn thành nhưng không có dữ liệu kết quả được lưu.', 'info')
            return redirect(url_for('main.task_list'))

        # Parse JSON kết quả
        try:
            results_data = json.loads(task.result)
            logger.debug(f"Đã parse thành công kết quả JSON cho task ID: {task_id}")
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi parse JSON kết quả của task ID {task_id}: {e}", exc_info=True)
            flash(f'Không thể đọc dữ liệu kết quả do lỗi định dạng JSON: {e}', 'danger')
            return redirect(url_for('main.task_list'))

        # Render template hiển thị kết quả
        return render_template('view_results.html',
                               title=f'Kết quả Tác vụ: {task.name}',
                               task=task,
                               results_data=results_data)

    except NoResultFound: # Mặc dù get() không raise lỗi này, để đây phòng trường hợp thay đổi logic query
        logger.warning(f"Truy cập xem kết quả cho task ID không tồn tại: {task_id}")
        abort(404)
    except Exception as e:
        logger.error(f"Lỗi không xác định khi xem kết quả task ID {task_id}: {e}", exc_info=True)
        flash('Đã xảy ra lỗi không mong muốn khi cố gắng hiển thị kết quả.', 'danger')
        return redirect(url_for('main.task_list'))

# === Route để tải kết quả Task dưới dạng CSV ===
@main.route('/tasks/<int:task_id>/download_csv')
def download_csv(task_id):
    """Xử lý yêu cầu tải xuống kết quả scraping dưới dạng file CSV."""
    try:
        task = db.session.get(Task, task_id)
        if not task:
            logger.warning(f"Yêu cầu tải CSV cho task ID không tồn tại: {task_id}")
            abort(404)

        if task.status != 'Completed' or not task.result:
            logger.info(f"Task ID {task_id} chưa hoàn thành hoặc không có kết quả. Không thể tải CSV.")
            flash('Tác vụ chưa hoàn thành, thất bại hoặc không có kết quả để tải xuống.', 'warning')
            return redirect(url_for('main.task_list'))

        try:
            results_data = json.loads(task.result)
            logger.debug(f"Đã parse thành công kết quả JSON cho CSV của task ID: {task_id}")
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi parse JSON kết quả CSV của task ID {task_id}: {e}", exc_info=True)
            flash(f'Không thể tạo CSV do lỗi định dạng JSON trong kết quả: {e}', 'danger')
            return redirect(url_for('main.view_results', task_id=task_id)) # Chuyển về trang xem kết quả

        # Kiểm tra xem results_data có phải là list các dict không (phổ biến)
        # hoặc chỉ là một dict đơn lẻ.
        if not results_data:
             flash('Không có dữ liệu để tạo file CSV.', 'info')
             return redirect(url_for('main.view_results', task_id=task_id))

        output = io.StringIO() # Tạo bộ đệm trong bộ nhớ
        # Ghi UTF-8 BOM để cải thiện tương thích với Excel
        output.write('\ufeff')

        fieldnames = []

        # Xử lý trường hợp kết quả là một list các dictionary
        if isinstance(results_data, list) and len(results_data) > 0 and isinstance(results_data[0], dict):
            fieldnames = list(results_data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results_data)
        # Xử lý trường hợp kết quả là một dictionary đơn lẻ
        elif isinstance(results_data, dict):
             fieldnames = list(results_data.keys())
             writer = csv.DictWriter(output, fieldnames=fieldnames)
             writer.writeheader()
             # Chuyển đổi dict đơn lẻ thành list chứa dict đó để writerows hoạt động
             writer.writerow(results_data)
        else:
            # Trường hợp dữ liệu không rõ cấu trúc (không phải list dict hoặc dict)
             logger.warning(f"Cấu trúc dữ liệu kết quả của task ID {task_id} không được hỗ trợ để tạo CSV.")
             flash('Định dạng dữ liệu kết quả không phù hợp để tạo CSV.', 'warning')
             return redirect(url_for('main.view_results', task_id=task_id))

        output.seek(0) # Đưa con trỏ về đầu bộ đệm

        # Tạo Response để trả về file CSV
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=task_{task.id}_{task.name}_results.csv'
        response.headers['Content-type'] = 'text/csv; charset=utf-8' # Thêm charset=utf-8
        logger.info(f"Đã tạo và gửi file CSV cho task ID: {task_id}")
        return response

    except Exception as e:
        logger.error(f"Lỗi không xác định khi tạo CSV cho task ID {task_id}: {e}", exc_info=True)
        flash('Đã xảy ra lỗi không mong muốn khi cố gắng tạo file CSV.', 'danger')
        return redirect(url_for('main.task_list'))

# === Route để xem chi tiết lỗi Task ===
@main.route('/tasks/<int:task_id>/error')
def view_error(task_id):
    """Route để hiển thị thông tin lỗi của một Task đã thất bại."""
    try:
        task = db.session.get(Task, task_id)
        if not task:
            logger.warning(f"Truy cập xem lỗi cho task ID không tồn tại: {task_id}")
            abort(404)

        if task.status != 'Failed':
            logger.info(f"Task ID {task_id} không ở trạng thái Failed (trạng thái: {task.status}). Không có lỗi để xem.")
            flash('Tác vụ không ở trạng thái thất bại. Không có thông tin lỗi.', 'warning')
            return redirect(url_for('main.task_list'))

        if not task.error_message:
            logger.info(f"Task ID {task_id} ở trạng thái Failed nhưng không có thông báo lỗi.")
            flash('Tác vụ đã thất bại nhưng không ghi nhận được thông báo lỗi cụ thể.', 'info')
            return redirect(url_for('main.task_list'))

        return render_template('view_error.html',
                               title=f'Lỗi Tác vụ: {task.name}',
                               task=task)
    except Exception as e:
        logger.error(f"Lỗi không xác định khi xem lỗi task ID {task_id}: {e}", exc_info=True)
        flash('Đã xảy ra lỗi không mong muốn khi cố gắng hiển thị thông tin lỗi.', 'danger')
        return redirect(url_for('main.task_list'))

# === Routes cho Chatbot ===
@main.route('/chatbot')
def chatbot_interface():
    """Hiển thị giao diện Chatbot."""
    return render_template('chatbot.html', title='Hỏi Đáp Chatbot')

@main.route('/ask_bot', methods=['POST'])
@csrf.exempt # Miễn trừ route này khỏi kiểm tra CSRF
def ask_bot():
    """API endpoint để nhận câu hỏi từ user và trả về câu trả lời từ bot."""
    # Lấy dữ liệu JSON từ request
    data = request.get_json()
    if not data or 'message' not in data:
        logger.warning("Request /ask_bot thiếu trường 'message' trong JSON.")
        return jsonify({'error': 'Missing message field'}), 400 # Bad Request

    user_message = data['message']
    logger.debug(f"Nhận được tin nhắn từ user: {user_message}")

    # Kiểm tra nội dung tin nhắn
    if not user_message.strip():
        logger.info("Request /ask_bot có tin nhắn rỗng.")
        return jsonify({'response': 'Vui lòng nhập câu hỏi.'}), 200 # Trả về OK nhưng yêu cầu nhập lại

    # Gọi hàm xử lý logic chatbot
    try:
        bot_response = get_bot_response(user_message)
        logger.debug(f"Bot phản hồi: {bot_response}")
        return jsonify({'response': bot_response})
    except Exception as e:
        logger.error(f"Lỗi khi gọi get_bot_response: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500 # Internal Server Error

# Các route khác sẽ được thêm vào đây...