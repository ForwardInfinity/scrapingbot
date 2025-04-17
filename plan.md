# Kế hoạch Triển khai (Implementation Plan) - Web Scraping Bot Nâng cao

**Dựa trên PRD phiên bản:** 2.0

## Phase 1: Thiết lập Môi trường và Dự án Nâng cao

*   **Mục tiêu:** Chuẩn bị môi trường phát triển, tạo cấu trúc dự án Flask nâng cao (với Service Layer, tests, Docker), cài đặt tất cả thư viện cần thiết và xây dựng layout giao diện cơ bản.
*   **Tasks:**
    *   **1.1:** Tạo thư mục gốc cho dự án (ví dụ: `web-scraping-bot`).
    *   **1.2:** Bên trong thư mục gốc, tạo môi trường ảo Python: `python -m venv venv`.
    *   **1.3:** Kích hoạt môi trường ảo: `venv\Scripts\activate`
    *   **1.4:** Cài đặt các thư viện Python cốt lõi và mở rộng: `pip install Flask Flask-SQLAlchemy Flask-WTF APScheduler requests beautifulsoup4 python-dotenv gunicorn pytest pytest-cov flake8 black email-validator validators`.
    *   **1.5:** Tạo cấu trúc thư mục dự án nâng cao như đã định nghĩa trong PRD v2.0 (mục 10), bao gồm các thư mục `app`, `app/services`, `app/utils`, `app/static`, `app/templates`, `app/templates/includes`, `app/templates/errors`, `tests`, `logs`, `instance`.
    *   **1.6:** Tạo các file khởi tạo cơ bản: `run.py`, `config.py`, `app/__init__.py`, `app/routes.py`, `app/models.py`, `app/forms.py`, `app/services/__init__.py`, `app/utils/__init__.py`, `tests/__init__.py`, `tests/conftest.py`.
    *   **1.7:** Tạo file `.gitignore` chuẩn cho Python/Flask, bao gồm `venv/`, `instance/`, `logs/`, `*.pyc`, `__pycache__/`, `.env`.
    *   **1.8:** Tạo file `.env.example` và `.env` (được gitignore). Định nghĩa các biến môi trường cơ bản trong `.env`: `FLASK_APP=run.py`, `FLASK_ENV=development`, `SECRET_KEY='your-strong-secret-key'`, `SQLALCHEMY_DATABASE_URI='sqlite:///../instance/app.db'`.
    *   **1.9:** Tạo file `.flaskenv` với nội dung `FLASK_APP=run.py` và `FLASK_ENV=development`.
    *   **1.10:** Cấu hình Flask app cơ bản trong `app/__init__.py`: Khởi tạo `Flask`, load cấu hình từ `config.py` và biến môi trường, khởi tạo extensions `SQLAlchemy`, `APScheduler`. Thiết lập cấu hình logging cơ bản (ghi ra console).
    *   **1.11:** Tạo file `config.py` với các lớp `Config`, `DevelopmentConfig`, `ProductionConfig`, `TestingConfig` chứa các cấu hình tương ứng (SECRET_KEY, DATABASE_URI, DEBUG, TESTING, SCHEDULER_API_ENABLED).
    *   **1.12:** Tạo file `run.py` ở thư mục gốc để khởi chạy Flask development server, import `app` từ `app/__init__.py`.
    *   **1.13:** Tạo file layout cơ sở `app/templates/base.html` sử dụng Bootstrap 5 (từ CDN). Layout này bao gồm cấu trúc HTML5, liên kết CSS/JS Bootstrap, định nghĩa các khối `title`, `head_css`, `content`, `body_scripts`. Tích hợp khu vực hiển thị thông báo flash (`_flashes.html`).
    *   **1.14:** Tạo file partial `app/templates/includes/_sidebar.html` chứa mã HTML cho thanh điều hướng bên trái với các liên kết đến "Dashboard", "Tạo tác vụ mới", "Danh sách tác vụ", "Hỏi Đáp Chatbot". Include sidebar này vào `base.html`.
    *   **1.15:** Tạo file partial `app/templates/includes/_flashes.html` để hiển thị các thông báo flash của Flask.
    *   **1.16:** Tạo route `/` trong `app/routes.py` để hiển thị trang Dashboard. Route này gọi một hàm service (ví dụ: `get_dashboard_stats()` từ `task_service.py`) để lấy dữ liệu thống kê (ban đầu là giả).
    *   **1.17:** Tạo file service `app/services/task_service.py` với hàm `get_dashboard_stats()` trả về dữ liệu thống kê giả.
    *   **1.18:** Tạo template `app/templates/dashboard.html` kế thừa từ `base.html`. Hiển thị tiêu đề "Tổng quan Web Scraping Bot", các thẻ thống kê Bootstrap (dữ liệu từ service) và nút "+ Tạo tác vụ Scraping mới".
    *   **1.19:** Chạy thử ứng dụng (`flask run`) và kiểm tra trang Dashboard hiển thị đúng layout, sidebar, và dữ liệu thống kê giả.

## Phase 2: Xây dựng Chức năng Quản lý Tác vụ (CRUD Nâng cao)

*   **Mục tiêu:** Implement các chức năng tạo, xem danh sách, sửa, xóa tác vụ scraping với form nhập liệu nâng cao cho selectors và validation.
*   **Tasks:**
    *   **2.1:** Định nghĩa model `Task` trong `app/models.py` sử dụng Flask-SQLAlchemy. Model bao gồm các trường: `id` (Integer, PK), `name` (String, Not Null), `url` (String, Not Null), `selectors` (Text/JSON, Not Null), `schedule` (String, Nullable), `status` (String, Default='Pending', Not Null), `created_at` (DateTime, Default=now), `updated_at` (DateTime, Default=now, OnUpdate=now), `last_run` (DateTime, Nullable), `result` (Text, Nullable), `error_message` (Text, Nullable).
    *   **2.2:** Sử dụng Flask shell (`flask shell`) để tạo các bảng trong cơ sở dữ liệu SQLite: `from app import db`, `db.create_all()`. Xác nhận file `instance/app.db` được tạo/cập nhật.
    *   **2.3:** Định nghĩa form `TaskForm` trong `app/forms.py` sử dụng Flask-WTF. Form bao gồm các trường: `name` (StringField, validators=[DataRequired()]), `url` (URLField, validators=[DataRequired(), URL()]), `selectors` (FieldList(FormField(SelectorForm)), validators=[DataRequired()]), `schedule_type` (SelectField với các lựa chọn lập lịch), `schedule_value` (StringField, tùy chọn). Sử dụng `SelectorForm` con cho các cặp Tên dữ liệu - Selector.
    *   **2.4:** Định nghĩa form con `SelectorForm` trong `app/forms.py` với các trường `data_name` (StringField, validators=[DataRequired()]) và `css_selector` (StringField, validators=[DataRequired()]).
    *   **2.5:** Tạo route `/tasks/new` (GET, POST) trong `app/routes.py` để xử lý việc tạo tác vụ mới.
    *   **2.6:** Tạo template `app/templates/task_form.html` kế thừa từ `base.html`. Template này render `TaskForm` sử dụng các macro của Flask-WTF/Bootstrap. Implement JavaScript để cho phép người dùng thêm/xóa động các trường nhập liệu cho selectors (sử dụng FieldList của WTForms).
    *   **2.7:** Tạo service function `create_task(form_data)` trong `app/services/task_service.py`. Hàm này nhận dữ liệu đã validate từ form, tạo đối tượng `Task` (chuyển đổi selectors thành JSON), lưu vào DB (`db.session.add()`, `db.session.commit()`), và trả về đối tượng Task đã tạo hoặc None nếu lỗi.
    *   **2.8:** Implement logic trong route `/tasks/new`:
        *   GET: Khởi tạo form rỗng và render `task_form.html`.
        *   POST: Validate form (`form.validate_on_submit()`). Nếu hợp lệ, gọi `task_service.create_task(form.data)`, hiển thị thông báo thành công (`flash()`), và chuyển hướng đến `/tasks`. Nếu không hợp lệ, render lại `task_form.html` với lỗi validation.
    *   **2.9:** Tạo route `/tasks` (GET) trong `app/routes.py` để hiển thị danh sách tác vụ.
    *   **2.10:** Tạo service function `get_tasks(page, per_page, search_term=None)` trong `app/services/task_service.py`. Hàm này truy vấn tác vụ từ DB, hỗ trợ tìm kiếm theo tên (`Task.name.ilike(...)`) và phân trang (`Task.query.paginate(...)`). Trả về đối tượng Pagination.
    *   **2.11:** Implement logic trong route `/tasks`: Lấy tham số `page` và `search` từ query string, gọi `task_service.get_tasks()`, và truyền đối tượng Pagination vào template.
    *   **2.12:** Tạo template `app/templates/task_list.html` kế thừa từ `base.html`. Hiển thị ô tìm kiếm, bảng HTML các tác vụ (lấy từ `pagination.items`) với các cột theo PRD, và các điều khiển phân trang (sử dụng `pagination` object).
    *   **2.13:** Tạo route `/tasks/<int:task_id>/edit` (GET, POST) trong `app/routes.py` để sửa tác vụ.
    *   **2.14:** Tạo service function `get_task_by_id(task_id)` và `update_task(task_id, form_data)` trong `app/services/task_service.py`.
    *   **2.15:** Implement logic trong route `/tasks/<int:task_id>/edit`:
        *   GET: Lấy task bằng ID, điền dữ liệu vào form, render `task_form.html`.
        *   POST: Validate form, gọi `task_service.update_task()`, flash thông báo, redirect về `/tasks`.
    *   **2.16:** Tạo route `/tasks/<int:task_id>/delete` (POST) trong `app/routes.py` để xóa tác vụ.
    *   **2.17:** Tạo service function `delete_task(task_id)` trong `app/services/task_service.py`.
    *   **2.18:** Implement logic trong route `/tasks/<int:task_id>/delete`: Gọi `task_service.delete_task()`, flash thông báo, redirect về `/tasks`. Thêm JavaScript `confirm()` vào nút xóa trong `task_list.html`.
    *   **2.19:** Kiểm tra kỹ lưỡng các chức năng: Tạo (với selectors động), Xem danh sách (với tìm kiếm, phân trang), Sửa, Xóa tác vụ. Đảm bảo validation hoạt động.

## Phase 3: Xây dựng Chức năng Scraping Linh hoạt & Bất đồng bộ

*   **Mục tiêu:** Implement logic scraping sử dụng CSS selectors do người dùng định nghĩa, chạy tác vụ bất đồng bộ để không chặn UI, và xử lý lỗi chi tiết.
*   **Tasks:**
    *   **3.1:** Tạo file `app/scraper.py`. Viết hàm `scrape_data(url, selectors_dict, timeout=30)` bên trong file này.
        *   Hàm nhận URL, dictionary selectors (`{'Tên dữ liệu': 'selector', ...}`) và timeout.
        *   Sử dụng `requests.get(url, timeout=timeout)` để tải HTML. Xử lý các exception của requests (Timeout, ConnectionError). Kiểm tra status code (raise exception nếu là 4xx/5xx).
        *   Sử dụng `BeautifulSoup(html_content, 'html.parser')` để phân tích HTML.
        *   Lặp qua `selectors_dict`, sử dụng `soup.select(selector)` để tìm các element. Xử lý trường hợp selector không tìm thấy element. Trích xuất text hoặc attribute mong muốn.
        *   Trả về một dictionary chứa dữ liệu scrape được (`{'Tên dữ liệu': 'giá trị' hoặc ['list', 'of', 'values'], ...}`).
        *   Nếu có bất kỳ lỗi nào trong quá trình (request lỗi, parse lỗi, selector lỗi), hàm nên raise một Exception cụ thể (ví dụ: `ScrapingError`) với thông điệp lỗi rõ ràng.
    *   **3.2:** Tạo file service `app/services/scraping_service.py`. Viết hàm `run_scraping_task(task_id)`.
        *   Hàm này được thiết kế để chạy bất đồng bộ (ví dụ: bởi APScheduler hoặc trong một thread riêng).
        *   Lấy đối tượng `Task` từ DB bằng `task_id`.
        *   Cập nhật trạng thái task thành 'Running' (`task.status = 'Running'`, `db.session.commit()`).
        *   Parse chuỗi JSON `task.selectors` thành dictionary Python.
        *   Gọi hàm `scraper.scrape_data(task.url, selectors_dict)`.
        *   Sử dụng `try...except` để bắt `ScrapingError` hoặc các Exception khác từ `scrape_data`.
        *   Nếu thành công:
            *   Chuyển dictionary kết quả thành chuỗi JSON.
            *   Cập nhật `task.result = result_json`, `task.status = 'Completed'`, `task.error_message = None`, `task.last_run = datetime.utcnow()`.
        *   Nếu thất bại (bắt được Exception):
            *   Lấy thông điệp lỗi từ Exception.
            *   Cập nhật `task.result = None`, `task.status = 'Failed'`, `task.error_message = error_message`, `task.last_run = datetime.utcnow()`.
        *   Commit thay đổi vào DB (`db.session.commit()`).
        *   *Lưu ý:* Cần xử lý context của Flask (app context, request context) nếu chạy trong thread/scheduler tách biệt. Sử dụng `with app.app_context():`.
    *   **3.3:** Tạo route `/tasks/<int:task_id>/run` (POST) trong `app/routes.py` để kích hoạt chạy tác vụ thủ công.
    *   **3.4:** Implement logic trong route `/tasks/<int:task_id>/run`:
        *   Lấy `Task` bằng ID.
        *   **Quyết định:** Sử dụng `APScheduler` để thêm một job chạy ngay lập tức (one-off job) gọi hàm `scraping_service.run_scraping_task(task_id)`. Điều này đảm bảo tính nhất quán với việc chạy lập lịch và xử lý context.
        *   Cập nhật trạng thái task thành 'Pending' (nếu cần) để người dùng biết job đã được đưa vào hàng đợi.
        *   Flash thông báo "Đã yêu cầu chạy tác vụ." và redirect về `/tasks`.
    *   **3.5:** Cập nhật `task_list.html`: Thêm nút "Chạy ngay". Thêm JavaScript để hiển thị spinner hoặc thông báo khi nút được nhấn và chờ phản hồi (hoặc chỉ cần redirect và để trạng thái cập nhật sau).

## Phase 4: Xây dựng Chức năng Lập lịch & Hiển thị Kết quả/Lỗi

*   **Mục tiêu:** Implement chức năng lập lịch chạy tác vụ tự động bằng APScheduler và xây dựng giao diện xem chi tiết kết quả hoặc lỗi của tác vụ.
*   **Tasks:**
    *   **4.1:** Cấu hình `APScheduler` trong `app/__init__.py`. Khởi tạo `BackgroundScheduler` và start nó. Đảm bảo scheduler hoạt động đúng trong môi trường Flask/Gunicorn.
    *   **4.2:** Sửa đổi service `task_service.create_task` và `task_service.update_task`:
        *   Khi tạo/sửa task, nếu người dùng chọn lập lịch (`schedule_type` != 'none'), phân tích `schedule_type` và `schedule_value` để tạo cấu hình trigger cho APScheduler (ví dụ: `trigger='interval'`, `hours=X` hoặc `trigger='cron'`, `hour=Y`).
        *   Sử dụng `scheduler.add_job()` để thêm hoặc `scheduler.modify_job()` để sửa job trong APScheduler. ID của job nên liên kết với `task.id` (ví dụ: `job_id=f'task_{task.id}'`). Hàm được gọi là `scraping_service.run_scraping_task` với `args=[task.id]`.
        *   Lưu thông tin lịch trình (`schedule_type`, `schedule_value`) vào trường `task.schedule`.
        *   Nếu người dùng bỏ lập lịch, sử dụng `scheduler.remove_job()` để xóa job tương ứng.
    *   **4.3:** Sửa đổi service `task_service.delete_task`: Trước khi xóa task khỏi DB, gọi `scheduler.remove_job(f'task_{task_id}', ignore_errors=True)` để xóa job tương ứng khỏi scheduler.
    *   **4.4:** Tạo route `/tasks/<int:task_id>/results` (GET) trong `app/routes.py`.
    *   **4.5:** Implement logic trong route `/tasks/<int:task_id>/results`:
        *   Lấy `Task` bằng ID.
        *   Kiểm tra nếu `task.result` không rỗng và `task.status == 'Completed'`.
        *   Parse chuỗi JSON `task.result` thành dictionary Python.
        *   Render template `view_results.html`, truyền vào thông tin task và dữ liệu kết quả đã parse.
        *   Nếu không có kết quả, redirect về `/tasks` với thông báo lỗi.
    *   **4.6:** Tạo template `app/templates/view_results.html` kế thừa từ `base.html`. Hiển thị thông tin tóm tắt tác vụ và trình bày dữ liệu kết quả (đã parse từ JSON) dưới dạng bảng HTML. Thêm nút "Tải xuống CSV".
    *   **4.7:** Tạo route `/tasks/<int:task_id>/download_csv` (GET) trong `app/routes.py`.
    *   **4.8:** Implement logic trong route `/tasks/<int:task_id>/download_csv`:
        *   Lấy `Task` và parse `task.result` JSON.
        *   Sử dụng module `csv` và `io.StringIO` để tạo nội dung file CSV trong bộ nhớ từ dữ liệu. Header của CSV là các key trong dictionary kết quả (Tên dữ liệu).
        *   Tạo `Response` của Flask, thiết lập header `Content-Disposition` (`attachment; filename=task_<id>_results.csv`) và `Content-Type` (`text/csv`).
        *   Trả về `Response` chứa nội dung CSV.
    *   **4.9:** Tạo route `/tasks/<int:task_id>/error` (GET) trong `app/routes.py`.
    *   **4.10:** Implement logic trong route `/tasks/<int:task_id>/error`:
        *   Lấy `Task` bằng ID.
        *   Kiểm tra nếu `task.error_message` không rỗng và `task.status == 'Failed'`.
        *   Render template `view_error.html`, truyền vào thông tin task và `task.error_message`.
        *   Nếu không có lỗi, redirect về `/tasks`.
    *   **4.11:** Tạo template `app/templates/view_error.html` kế thừa từ `base.html`. Hiển thị thông tin tóm tắt tác vụ và thông điệp lỗi `error_message`.
    *   **4.12:** Cập nhật `task_list.html`: Thêm nút "Xem kết quả" (liên kết đến `/tasks/<id>/results`) chỉ hiển thị khi status là 'Completed'. Thêm nút "Xem lỗi" (liên kết đến `/tasks/<id>/error`) chỉ hiển thị khi status là 'Failed'.
    *   **4.13:** Kiểm tra kỹ lưỡng chức năng lập lịch (tạo job, sửa job, xóa job), xem kết quả, tải CSV, xem lỗi.

## Phase 5: Tích hợp Chatbot Hướng dẫn (Rule-Based)

*   **Mục tiêu:** Xây dựng và tích hợp chatbot đơn giản sử dụng Rule-Based Engine tự xây dựng để trả lời câu hỏi về ứng dụng.
*   **Tasks:**
    *   **5.1:** Tạo file `app/chatbot_logic.py`.
    *   **5.2:** Thiết kế cấu trúc dữ liệu cho các quy tắc (ví dụ: list các dictionary `{'keywords': ['tạo', 'task', 'mới'], 'response': 'Để tạo task mới, nhấn vào nút "Tạo tác vụ mới" trên sidebar...'}`).
    *   **5.3:** Viết hàm `get_bot_response(user_input)` trong `chatbot_logic.py`. Hàm này nhận câu hỏi của người dùng, chuẩn hóa input (lowercase, loại bỏ dấu câu), tìm quy tắc phù hợp nhất dựa trên keywords, và trả về câu trả lời tương ứng hoặc một câu trả lời mặc định nếu không tìm thấy.
    *   **5.4:** Xây dựng bộ quy tắc ban đầu trong `chatbot_logic.py` bao gồm các câu hỏi/đáp về: tạo task, thêm selector, lập lịch, xem kết quả, xem lỗi, tải CSV.
    *   **5.5:** Tạo route `/chatbot` (GET) trong `app/routes.py` để hiển thị giao diện chatbot.
    *   **5.6:** Tạo template `app/templates/chatbot.html` kế thừa từ `base.html`. Template chứa:
        *   Một `div` để hiển thị lịch sử hội thoại (có scroll).
        *   Một form với ô nhập liệu (`input type="text"`) và nút "Gửi".
    *   **5.7:** Tạo route API `/ask_bot` (POST) trong `app/routes.py`. Route này nhận JSON `{'message': '...'}` từ client.
    *   **5.8:** Implement logic trong route `/ask_bot`: Lấy `message`, gọi `chatbot_logic.get_bot_response(message)`, và trả về JSON `{'response': '...'}`.
    *   **5.9:** Thêm mã JavaScript (sử dụng Fetch API) vào `chatbot.html`:
        *   Bắt sự kiện submit form (ngăn chặn default).
        *   Lấy câu hỏi từ input, hiển thị trong vùng hội thoại.
        *   Gửi POST request đến `/ask_bot` với câu hỏi.
        *   Nhận phản hồi JSON, hiển thị câu trả lời của bot trong vùng hội thoại.
        *   Xóa nội dung input.
    *   **5.10:** Kiểm tra chức năng chatbot: Gửi các câu hỏi đã định nghĩa và câu hỏi không xác định, kiểm tra câu trả lời và giao diện hiển thị.

## Phase 6: Hoàn thiện UI/UX

*   **Mục tiêu:** Đảm bảo giao diện người dùng responsive, dễ sử dụng, cung cấp phản hồi tốt và có tính thẩm mỹ cao.
*   **Tasks:**
    *   **6.1:** Kiểm tra và tinh chỉnh tính responsive của tất cả các trang trên các kích thước màn hình khác nhau (desktop, tablet, mobile) sử dụng Developer Tools của trình duyệt. Ưu tiên sửa lỗi hiển thị trên mobile.
    *   **6.2:** Implement Toast Notifications (sử dụng Bootstrap Toasts) để thay thế hoặc bổ sung cho các thông báo flash, cung cấp phản hồi tức thì cho các hành động (lưu thành công, xóa thành công, yêu cầu chạy task, lỗi...).
    *   **6.3:** Implement Spinners (sử dụng Bootstrap Spinners) một cách nhất quán tại các vị trí cần thiết: khi nhấn nút "Chạy ngay", khi submit form tạo/sửa task, khi tải dữ liệu AJAX (nếu có).
    *   **6.4:** Rà soát và cải thiện thông báo lỗi validation trên các form, đảm bảo chúng rõ ràng và hiển thị đúng vị trí.
    *   **6.5:** Tinh chỉnh giao diện bảng `task_list.html`: Đảm bảo các cột hiển thị hợp lý, có thể thêm tooltip cho các icon/nút nếu cần.
    *   **6.6:** (Tùy chọn nâng cao) Implement chức năng Dark Mode/Light Mode toggle sử dụng JavaScript và CSS variables.

## Phase 7: Đảm bảo Chất lượng (Logging, Testing, Code Quality)

*   **Mục tiêu:** Nâng cao chất lượng và độ tin cậy của ứng dụng thông qua logging chi tiết, unit testing và tuân thủ chuẩn code.
*   **Tasks:**
    *   **7.1:** Cấu hình hệ thống Logging chi tiết trong `app/__init__.py`:
        *   Sử dụng `logging.basicConfig` hoặc cấu hình dictionary.
        *   Thiết lập `RotatingFileHandler` để ghi log vào file `logs/app.log` với kích thước tối đa và số lượng file backup.
        *   Thiết lập `StreamHandler` để ghi log ra console (cho development).
        *   Định dạng log bao gồm timestamp, level, module, message.
        *   Đặt level log phù hợp cho development (DEBUG) và production (INFO/WARNING).
    *   **7.2:** Thêm các câu lệnh log (`current_app.logger.info()`, `.warning()`, `.error()`, `.debug()`) vào các vị trí quan trọng trong code (routes, services, scraper): khởi động app, xử lý request, gọi service, chạy task, bắt exception...
    *   **7.3:** Viết Unit Tests sử dụng `pytest`:
        *   Tạo các file test trong thư mục `tests/` (ví dụ: `test_models.py`, `test_task_service.py`, `test_scraper.py`, `test_routes.py`).
        *   Viết test case cho các model (khởi tạo, thuộc tính).
        *   Viết test case cho các hàm trong services (logic nghiệp vụ, tương tác DB giả lập - có thể dùng `unittest.mock` hoặc fixture DB riêng cho test).
        *   Viết test case cho hàm `scrape_data` (giả lập `requests.get`, `BeautifulSoup`).
        *   Viết test case cho các route cơ bản (kiểm tra status code, nội dung trả về - sử dụng `app.test_client()`).
        *   Sử dụng fixtures trong `conftest.py` để tạo app context, test client, dữ liệu giả.
    *   **7.4:** Cấu hình `pytest-cov` để đo lường code coverage. Chạy test với lệnh `pytest --cov=app`. Đảm bảo coverage đạt tối thiểu 80%.
    *   **7.5:** Cấu hình `flake8` (trong file `.flake8`) để kiểm tra code style và lỗi. Chạy `flake8 .` để kiểm tra.
    *   **7.6:** Cấu hình `black` (trong file `pyproject.toml` nếu cần). Chạy `black .` để tự động format code.
    *   **7.7:** Sửa tất cả các lỗi và cảnh báo từ `flake8` và đảm bảo code được format bởi `black`.

## Phase 8: Đóng gói Docker & Thiết lập CI/CD

*   **Mục tiêu:** Đóng gói ứng dụng bằng Docker để dễ dàng triển khai và thiết lập pipeline CI/CD cơ bản trên GitHub Actions.
*   **Tasks:**
    *   **8.1:** Viết `Dockerfile`:
        *   Chọn base image Python phù hợp (ví dụ: `python:3.9-slim`).
        *   Thiết lập working directory.
        *   Copy `requirements.txt` và cài đặt dependencies.
        *   Copy toàn bộ mã nguồn ứng dụng vào image.
        *   Expose port mà Gunicorn sẽ chạy (ví dụ: 5000).
        *   Thiết lập entrypoint hoặc command để chạy ứng dụng bằng Gunicorn (ví dụ: `gunicorn -b :5000 run:app`).
    *   **8.2:** Viết `docker-compose.yml`:
        *   Định nghĩa service `web` sử dụng image build từ `Dockerfile`.
        *   Map port (ví dụ: `8080:5000`).
        *   Mount volume cho `instance/` và `logs/` để dữ liệu và log được lưu trữ bên ngoài container.
        *   Sử dụng `.env` file để truyền biến môi trường vào container.
    *   **8.3:** Build và chạy thử ứng dụng bằng Docker Compose: `docker-compose build`, `docker-compose up`. Truy cập `http://localhost:8080` để kiểm tra.
    *   **8.4:** Tạo workflow CI/CD trong `.github/workflows/main.yml` (GitHub Actions):
        *   **Trigger:** `on: [push, pull_request]` cho nhánh `main` và `develop`.
        *   **Jobs:**
            *   `lint`: Setup Python, cài `flake8`, chạy `flake8 .`.
            *   `test`: Setup Python, cài dependencies từ `requirements.txt`, chạy `pytest --cov=app`. (Tùy chọn: Upload coverage report lên Codecov/Coveralls).
            *   `build` (chỉ chạy khi push vào `main`): Login vào Docker Hub (sử dụng secrets), build Docker image, tag image, push image lên Docker Hub.
    *   **8.5:** Commit các file Docker, docker-compose, workflow vào Git. Kiểm tra trạng thái CI trên GitHub Actions.

## Phase 9: Triển khai & Hoàn thiện Tài liệu

*   **Mục tiêu:** Triển khai ứng dụng lên môi trường production (PythonAnywhere) và hoàn thiện tài liệu dự án (README, Report).
*   **Tasks:**
    *   **9.1:** **Triển khai lên PythonAnywhere:**
        *   Tạo tài khoản miễn phí/trả phí trên PythonAnywhere.
        *   Upload mã nguồn (Git clone hoặc upload zip).
        *   Tạo Web App mới (Flask, Python 3.9).
        *   Cấu hình Source code, Working directory.
        *   Mở Bash console, tạo/kích hoạt virtualenv, cài dependencies (`pip install -r requirements.txt`).
        *   Chỉnh sửa file WSGI để import đúng `app` và cấu hình Gunicorn (nếu cần, hoặc dùng uWSGI mặc định).
        *   Đảm bảo đường dẫn database SQLite trong cấu hình là đường dẫn tuyệt đối trên server.
        *   Thiết lập biến môi trường (SECRET_KEY...) trong tab "Web" -> "Environment variables".
        *   Reload Web App và kiểm tra ứng dụng trên URL `<yourusername>.pythonanywhere.com`. Test lại các chức năng chính.
    *   **9.2:** Hoàn thiện file `README.md`:
        *   Viết mô tả chi tiết dự án, mục tiêu, công nghệ.
        *   Cung cấp hướng dẫn cài đặt, chạy local (Flask & Docker), chạy test.
        *   Giải thích cấu trúc thư mục.
        *   Thêm hướng dẫn sử dụng các chức năng chính (kèm ảnh chụp màn hình hoặc GIF).
        *   Thêm hướng dẫn triển khai (PythonAnywhere & Docker).
        *   Thêm badge CI từ GitHub Actions.
        *   Thêm link demo (PythonAnywhere URL).
    *   **9.3:** (Khuyến khích) Viết báo cáo `docs/Report.pdf` chi tiết theo cấu trúc đề xuất trong PRD.
    *   **9.4:** Rà soát toàn bộ mã nguồn lần cuối: Kiểm tra lỗi, tối ưu nhỏ, đảm bảo tính nhất quán, thêm các comment cần thiết.
    *   **9.5:** Tạo file `requirements.txt` cuối cùng bằng lệnh: `pip freeze > requirements.txt`. Kiểm tra lại nội dung file này.
    *   **9.6:** Chuẩn bị cho buổi bảo vệ: Nắm vững kiến trúc, luồng hoạt động, lý do chọn công nghệ, các chức năng mở rộng, kết quả test, quy trình Docker/CI/CD. Chuẩn bị câu trả lời cho các câu hỏi "hỏi xoáy" tiềm năng.