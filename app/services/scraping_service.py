import json
from datetime import datetime, timezone
from app import db, create_app # Import db và create_app để tạo app_context
from app.models import Task
from app.scraper import scrape_data, ScrapingError
import logging

logger = logging.getLogger(__name__)


def run_scraping_task(task_id: int):
    """
    Hàm chạy một tác vụ scraping cụ thể, cập nhật trạng thái và kết quả/lỗi vào DB.
    Hàm này được thiết kế để chạy trong một context riêng (ví dụ: APScheduler job).

    Args:
        task_id: ID của tác vụ cần chạy.
    """
    # Tạo app context để có thể truy cập db và các cấu hình khác của Flask
    app = create_app()
    with app.app_context():
        task = db.session.get(Task, task_id)
        if not task:
            logger.error(f"Không tìm thấy task với ID: {task_id} để chạy.")
            return

        logger.info(f"Bắt đầu chạy tác vụ scraping ID: {task_id} - Tên: {task.name}")
        task.status = 'Running'
        task.last_run = datetime.now(timezone.utc)
        # Commit trạng thái Running trước khi thực hiện scrape
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật trạng thái 'Running' cho task ID: {task_id}. Lỗi: {e}", exc_info=True)
            db.session.rollback() # Rollback nếu có lỗi
            # Có thể quyết định dừng lại ở đây hoặc vẫn tiếp tục chạy scrape
            return # Dừng nếu không cập nhật được status

        try:
            # Parse selectors từ JSON string trong DB thành dict
            selectors_dict = json.loads(task.selectors)

            # Gọi hàm scrape_data
            scraped_result = scrape_data(task.url, selectors_dict)

            # Xử lý kết quả thành công
            task.result = json.dumps(scraped_result, ensure_ascii=False, indent=2) # Lưu JSON đẹp hơn
            task.status = 'Completed'
            task.error_message = None
            logger.info(f"Tác vụ scraping ID: {task_id} hoàn thành thành công.")

        except ScrapingError as e:
            # Xử lý lỗi scraping đã biết
            task.status = 'Failed'
            task.error_message = str(e)
            task.result = None # Xóa kết quả cũ nếu có
            logger.warning(f"Tác vụ scraping ID: {task_id} thất bại. Lỗi: {e}")
        except json.JSONDecodeError as e:
            # Xử lý lỗi khi parse JSON selectors từ DB
            task.status = 'Failed'
            task.error_message = f"Lỗi định dạng JSON trong Selectors: {e}"
            task.result = None
            logger.error(f"Lỗi parse JSON selectors cho task ID: {task_id}. Lỗi: {e}", exc_info=True)
        except Exception as e:
            # Xử lý các lỗi không mong muốn khác
            task.status = 'Failed'
            task.error_message = f"Lỗi không xác định: {str(e)}"
            task.result = None
            logger.error(f"Lỗi không xác định khi chạy task ID: {task_id}. Lỗi: {e}", exc_info=True)

        finally:
            # Cập nhật lại DB với kết quả cuối cùng (thành công hoặc thất bại)
            try:
                db.session.commit()
            except Exception as e:
                logger.error(f"Lỗi khi commit kết quả cuối cùng cho task ID: {task_id}. Lỗi: {e}", exc_info=True)
                db.session.rollback() 