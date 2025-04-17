# Task Track Progress - Web Scraping Bot Nâng cao

**Dựa trên Implementation Plan v2.0 (PRD v2.0)**

## IN PROGRESS

*   [ ] **6.1:** Kiểm tra và tinh chỉnh responsive trên các kích thước màn hình.
*   [ ] **6.2:** Implement Toast Notifications (Bootstrap Toasts) cho phản hồi hành động.
*   [ ] **6.3:** Implement Spinners (Bootstrap Spinners) nhất quán khi chạy nền/tải dữ liệu.
*   [ ] **6.4:** Rà soát và cải thiện thông báo lỗi validation trên form.

## PENDING

### Phase 6: Hoàn thiện UI/UX

*   [ ] **6.5:** Tinh chỉnh giao diện bảng `task_list.html` (cột, tooltip).
*   [ ] **6.6:** (Tùy chọn) Implement Dark Mode/Light Mode toggle.

### Phase 7: Đảm bảo Chất lượng (Logging, Testing, Code Quality)

*   [ ] **7.1:** Cấu hình Logging chi tiết (`RotatingFileHandler`, `StreamHandler`, format, level).
*   [ ] **7.2:** Thêm câu lệnh log vào các vị trí quan trọng trong code.
*   [ ] **7.3:** Viết Unit Tests (`pytest`) cho models, services, scraper, routes.
*   [ ] **7.4:** Cấu hình và chạy `pytest-cov`, đảm bảo coverage >= 80%.
*   [ ] **7.5:** Cấu hình và chạy `flake8` để kiểm tra code style.
*   [ ] **7.6:** Cấu hình và chạy `black` để format code.
*   [ ] **7.7:** Sửa lỗi/cảnh báo từ `flake8` và đảm bảo code đã được format.

### Phase 8: Đóng gói Docker & Thiết lập CI/CD

*   [ ] **8.1:** Viết `Dockerfile` (base image, copy code, install deps, expose port, run gunicorn).
*   [ ] **8.2:** Viết `docker-compose.yml` (service web, map port, volumes, env file).
*   [ ] **8.3:** Build và chạy thử ứng dụng bằng Docker Compose.
*   [ ] **8.4:** Tạo workflow CI/CD `.github/workflows/main.yml` (lint, test, build Docker image).
*   [ ] **8.5:** Commit file Docker, docker-compose, workflow. Kiểm tra CI trên GitHub Actions.

### Phase 9: Triển khai & Hoàn thiện Tài liệu

*   [ ] **9.1:** Triển khai lên PythonAnywhere (upload, setup venv, install deps, config web app, WSGI, env vars, reload, test).
*   [ ] **9.2:** Hoàn thiện `README.md` (đầy đủ các mục, ảnh chụp/GIF, badge CI, link demo).
*   [ ] **9.3:** (Khuyến khích) Viết báo cáo `docs/Report.pdf`.
*   [ ] **9.4:** Rà soát toàn bộ mã nguồn lần cuối.
*   [ ] **9.5:** Tạo file `requirements.txt` cuối cùng (`pip freeze`).
*   [ ] **9.6:** Chuẩn bị cho buổi bảo vệ (nắm vững dự án, chuẩn bị câu trả lời).

## DONE

### [x] Phase 1: Thiết lập Môi trường và Dự án Nâng cao (ĐÃ HOÀN THÀNH TOÀN BỘ PHASE NÀY)

*   [x] **1.1:** Tạo thư mục gốc dự án (`web-scraping-bot-enhanced`).
*   [x] **1.2:** Tạo môi trường ảo Python (`venv`).
*   [x] **1.3:** Kích hoạt môi trường ảo.
*   [x] **1.4:** Cài đặt các thư viện Python cốt lõi và mở rộng (Flask, SQLAlchemy, WTForms, APScheduler, requests, bs4, dotenv, gunicorn, pytest, cov, flake8, black, etc.).
*   [x] **1.5:** Tạo cấu trúc thư mục dự án nâng cao (app, services, utils, tests, logs, instance...).
*   [x] **1.6:** Tạo các file khởi tạo cơ bản (`run.py`, `config.py`, `app/__init__.py`, `routes.py`, `models.py`, `forms.py`, `services/__init__.py`, `utils/__init__.py`, `tests/__init__.py`, `conftest.py`).
*   [x] **1.7:** Tạo file `.gitignore` chuẩn.
*   [x] **1.8:** Tạo file `.env.example` và `.env` với các biến môi trường cơ bản. (Lưu ý: .env cần tạo thủ công do hạn chế tool)
*   [x] **1.9:** Tạo file `.flaskenv`.
*   [x] **1.10:** Cấu hình Flask app cơ bản (`app/__init__.py`) với extensions và logging console.
*   [x] **1.11:** Tạo file `config.py` với các lớp Config (Dev, Prod, Test).
*   [x] **1.12:** Tạo file `run.py` để khởi chạy server dev.
*   [x] **1.13:** Tạo layout cơ sở `base.html` (Bootstrap 5, blocks, flashes).
*   [x] **1.14:** Tạo và include sidebar `_sidebar.html`.
*   [x] **1.15:** Tạo partial `_flashes.html`.
*   [x] **1.16:** Tạo route `/` cho Dashboard (gọi service).
*   [x] **1.17:** Tạo service `task_service.py` với hàm `get_dashboard_stats()` (dữ liệu giả).
*   [x] **1.18:** Tạo template `dashboard.html` (kế thừa base, hiển thị stats, nút tạo task).
*   [x] **1.19:** Chạy thử và kiểm tra trang Dashboard.

### [x] Phase 2: Xây dựng Chức năng Quản lý Tác vụ (CRUD Nâng cao) (ĐÃ HOÀN THÀNH TOÀN BỘ PHASE NÀY)

*   [x] **2.1:** Định nghĩa model `Task` trong `models.py` (bao gồm selectors, schedule error_message...).
*   [x] **2.2:** Tạo bảng database (`db.create_all()`). (Đã hướng dẫn chạy lệnh thủ công)
*   [x] **2.3:** Định nghĩa form `TaskForm` trong `forms.py` (với FieldList cho selectors).
*   [x] **2.4:** Định nghĩa form con `SelectorForm` trong `forms.py`.
*   [x] **2.5:** Tạo route `/tasks/new` (GET, POST).
*   [x] **2.6:** Tạo template `task_form.html` (render form, JS cho selectors động).
*   [x] **2.7:** Tạo service function `create_task(form_data)` trong `app/services/task_service.py`.
*   [x] **2.8:** Implement logic route `/tasks/new` (validate, gọi service, flash, redirect).
*   [x] **2.9:** Tạo route `/tasks` (GET).
*   [x] **2.10:** Tạo service function `get_tasks(page, per_page, search_term)` (với search, pagination).
*   [x] **2.11:** Implement logic route `/tasks` (lấy params, gọi service, truyền pagination).
*   [x] **2.12:** Tạo template `task_list.html` (ô search, bảng task, pagination controls).
*   [x] **2.13:** Tạo route `/tasks/<int:task_id>/edit` (GET, POST).
*   [x] **2.14:** Tạo service functions `get_task_by_id(task_id)` và `update_task(task_id, form_data)`.
*   [x] **2.15:** Implement logic route `/tasks/<int:task_id>/edit` (lấy task, điền form, validate, gọi service, flash, redirect).
*   [x] **2.16:** Tạo route `/tasks/<int:task_id>/delete` (POST).
*   [x] **2.17:** Tạo service function `delete_task(task_id)`.
*   [x] **2.18:** Implement logic route `/tasks/<int:task_id>/delete` (gọi service, flash, redirect, JS confirm).
*   [x] **2.19:** Kiểm tra chức năng CRUD nâng cao (Tạo, Xem list, Search, Paginate, Sửa, Xóa).

### [x] Phase 3: Xây dựng Chức năng Scraping Linh hoạt & Bất đồng bộ (ĐÃ HOÀN THÀNH TOÀN BỘ PHASE NÀY)

*   [x] **3.1:** Tạo `app/scraper.py` và hàm `scrape_data(url, selectors_dict, timeout)` (requests, bs4, xử lý lỗi chi tiết, trả dict/raise exception).
*   [x] **3.2:** Tạo service `scraping_service.py` và hàm `run_scraping_task(task_id)` (chạy nền, cập nhật status, gọi scraper, xử lý kết quả/lỗi, lưu DB, xử lý app context).
*   [x] **3.3:** Tạo route `/tasks/<int:task_id>/run` (POST).
*   [x] **3.4:** Implement logic route `/tasks/<int:task_id>/run` (thêm job APScheduler chạy ngay, flash, redirect).
*   [x] **3.5:** Cập nhật `task_list.html` (nút "Chạy ngay", JS spinner/phản hồi).

### [x] Phase 4: Xây dựng Chức năng Lập lịch & Hiển thị Kết quả/Lỗi (ĐÃ HOÀN THÀNH TOÀN BỘ PHASE NÀY)

*   [x] **4.1:** Cấu hình và khởi động `APScheduler` trong `app/__init__.py`.
*   [x] **4.2:** Sửa đổi service `create_task` và `update_task` (thêm/sửa job APScheduler dựa trên form).
*   [x] **4.3:** Sửa đổi service `delete_task` (xóa job APScheduler tương ứng).
*   [x] **4.4:** Tạo route `/tasks/<int:task_id>/results` (GET).
*   [x] **4.5:** Implement logic route `/tasks/<int:task_id>/results` (lấy task, parse JSON, render template).
*   [x] **4.6:** Tạo template `view_results.html` (hiển thị kết quả dạng bảng, nút download CSV).
*   [x] **4.7:** Tạo route `/tasks/<int:task_id>/download_csv` (GET).
*   [x] **4.8:** Implement logic route `/tasks/<int:task_id>/download_csv` (lấy task, tạo CSV, trả Response).
*   [x] **4.9:** Tạo route `/tasks/<int:task_id>/error` (GET).
*   [x] **4.10:** Implement logic route `/tasks/<int:task_id>/error` (lấy task, render template).
*   [x] **4.11:** Tạo template `view_error.html` (hiển thị thông tin lỗi).
*   [x] **4.12:** Cập nhật `task_list.html` (thêm nút "Xem kết quả", "Xem lỗi" có điều kiện).
*   [x] **4.13:** Kiểm tra chức năng lập lịch, xem kết quả, tải CSV, xem lỗi. (Cần kiểm tra thủ công)

### [x] Phase 5: Tích hợp Chatbot Hướng dẫn (Rule-Based) (ĐÃ HOÀN THÀNH TOÀN BỘ PHASE NÀY)

*   [x] **5.1:** Tạo file `app/chatbot_logic.py`.
*   [x] **5.2:** Thiết kế cấu trúc dữ liệu quy tắc (keywords, response).
*   [x] **5.3:** Viết hàm `get_bot_response(user_input)` (chuẩn hóa, tìm quy tắc, trả lời).
*   [x] **5.4:** Xây dựng bộ quy tắc ban đầu cho các chức năng chính.
*   [x] **5.5:** Tạo route `/chatbot` (GET).
*   [x] **5.6:** Tạo template `chatbot.html` (vùng hội thoại, form input).
*   [x] **5.7:** Tạo route API `/ask_bot` (POST).
*   [x] **5.8:** Implement logic route `/ask_bot` (nhận JSON, gọi service, trả JSON).
*   [x] **5.9:** Thêm JavaScript vào `chatbot.html` (bắt submit, gọi API, hiển thị hội thoại).
*   [x] **5.10:** Kiểm tra chức năng chatbot.
