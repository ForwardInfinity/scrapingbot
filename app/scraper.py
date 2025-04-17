import requests
from bs4 import BeautifulSoup
import logging

# Lấy logger từ Flask app để ghi log thống nhất
logger = logging.getLogger(__name__)

class ScrapingError(Exception):
    """Custom exception cho các lỗi xảy ra trong quá trình scraping."""
    pass

def scrape_data(url: str, selectors_dict: dict, timeout: int = 30) -> dict:
    """
    Thực hiện lấy dữ liệu từ một URL dựa vào các CSS selector được cung cấp.

    Args:
        url: URL của trang web cần scrape.
        selectors_dict: Dictionary với key là tên dữ liệu, value là CSS selector.
                        Ví dụ: {'title': 'h1.title', 'price': '.product-price'}
        timeout: Thời gian tối đa (giây) chờ phản hồi từ server.

    Returns:
        Một dictionary chứa dữ liệu scrape được. Key là tên dữ liệu, value là
        giá trị text của element đầu tiên tìm thấy hoặc list các text nếu
        selector trả về nhiều element.

    Raises:
        ScrapingError: Nếu có lỗi xảy ra trong quá trình request, parse HTML,
                       hoặc không tìm thấy selector.
    """
    scraped_data = {}
    try:
        logger.info(f"Bắt đầu scrape dữ liệu từ URL: {url}")
        response = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'}) # Thêm User-Agent cơ bản
        response.raise_for_status() # Raise HTTPError cho status code 4xx/5xx

        soup = BeautifulSoup(response.content, 'html.parser')

        for data_name, selector in selectors_dict.items():
            logger.debug(f"Tìm kiếm selector: '{selector}' cho '{data_name}'")
            elements = soup.select(selector)

            if not elements:
                # Có thể quyết định trả về None/chuỗi rỗng hoặc raise lỗi
                # Ở đây chọn raise lỗi để báo hiệu task bị fail
                logger.warning(f"Không tìm thấy element nào với selector: '{selector}' tại URL: {url}")
                raise ScrapingError(f"Selector không tìm thấy: '{selector}'")

            # Lấy text từ các elements, loại bỏ khoảng trắng thừa
            # Nếu có nhiều element, trả về list text. Nếu chỉ có 1, trả về text đó.
            extracted_texts = [el.get_text(strip=True) for el in elements]

            if len(extracted_texts) == 1:
                scraped_data[data_name] = extracted_texts[0]
                logger.debug(f"Đã tìm thấy '{data_name}': {extracted_texts[0]}")
            else:
                scraped_data[data_name] = extracted_texts
                logger.debug(f"Đã tìm thấy danh sách '{data_name}': {len(extracted_texts)} items")

        logger.info(f"Scrape thành công từ URL: {url}. Dữ liệu: {list(scraped_data.keys())}")
        return scraped_data

    except requests.exceptions.Timeout:
        logger.error(f"Request timeout khi truy cập URL: {url}", exc_info=True)
        raise ScrapingError(f"Request Timeout ({timeout}s) cho URL: {url}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Lỗi request khi truy cập URL: {url}. Lỗi: {e}", exc_info=True)
        raise ScrapingError(f"Lỗi Request: {e}")
    except Exception as e:
        # Bắt các lỗi khác (ví dụ: lỗi parse của BeautifulSoup)
        logger.error(f"Lỗi không xác định khi scrape URL: {url}. Lỗi: {e}", exc_info=True)
        # Nếu không phải ScrapingError đã raise ở trên, bọc lại bằng ScrapingError
        if not isinstance(e, ScrapingError):
            raise ScrapingError(f"Lỗi không xác định: {e}")
        else:
            raise # Re-raise ScrapingError đã bắt được (vd: Selector không tìm thấy) 