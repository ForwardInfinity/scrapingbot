import re
import unicodedata

# 5.2: Thiết kế cấu trúc dữ liệu quy tắc (Rule-Based)
# Mỗi quy tắc là một dictionary chứa 'keywords' và 'response'
# 'keywords' là list các từ khóa. Một quy tắc được khớp nếu TẤT CẢ các từ khóa trong list xuất hiện trong input của người dùng.
# 'priority' (tùy chọn): Quy tắc có priority cao hơn sẽ được ưu tiên nếu có nhiều quy tắc khớp.
RULES = [
    # Tách quy tắc chào hỏi thành các quy tắc riêng lẻ
    {
        'keywords': ['chào', 'hello', 'hi', 'xin chào', 'chào bạn', 'chào mừng'],
        'response': 'Chào bạn! Tôi có thể giúp gì về việc sử dụng Web Scraping Bot?',
        'priority': 1
    },
    {
        'keywords': ['tạo', 'task', 'mới', 'tạo task', 'tạo tác vụ', 'tạo tác vụ mới'],
        'response': 'Để tạo tác vụ mới, bạn nhấn vào nút "Tạo tác vụ mới" trên thanh điều hướng bên trái hoặc nút "+ Tạo tác vụ Scraping mới" trên trang Dashboard.',
        'priority': 2
    },
    {
        'keywords': ['tạo', 'task'],
        'response': 'Để tạo tác vụ mới, bạn nhấn vào nút "Tạo tác vụ mới" trên thanh điều hướng bên trái hoặc nút "+ Tạo tác vụ Scraping mới" trên trang Dashboard.',
        'priority': 1
    },
    {
        'keywords': ['thêm', 'selector', 'css'],
        'response': 'Trong form tạo hoặc sửa tác vụ, bạn có thể thêm nhiều cặp "Tên dữ liệu" và "CSS Selector" tương ứng. Nhấn nút "Thêm Selector" để thêm dòng mới.',
        'priority': 2
    },
    {
        'keywords': ['thêm', 'selector'],
        'response': 'Trong form tạo hoặc sửa tác vụ, bạn có thể thêm nhiều cặp "Tên dữ liệu" và "CSS Selector" tương ứng. Nhấn nút "Thêm Selector" để thêm dòng mới.',
        'priority': 1
    },
     {
        'keywords': ['selector', 'là', 'gì'],
        'response': 'CSS Selector là một mẫu để chọn các phần tử HTML trên trang web. Bạn cần cung cấp selector chính xác để bot biết cần lấy dữ liệu nào (ví dụ: `#main-title`, `.product-price`).',
        'priority': 1
    },
    {
        'keywords': ['lập', 'lịch', 'chạy', 'task', 'tự động'],
        'response': 'Khi tạo hoặc sửa tác vụ, bạn có thể chọn "Cấu hình Lập lịch" để tác vụ tự động chạy theo khoảng thời gian (ví dụ: mỗi 2 giờ) hoặc vào một thời điểm cụ thể hàng ngày.',
        'priority': 2
    },
    {
        'keywords': ['xem', 'kết', 'quả', 'scrape'],
        'response': 'Khi một tác vụ hoàn thành (status "Completed"), bạn có thể nhấn nút "Xem kết quả" trong danh sách tác vụ để xem dữ liệu đã thu thập.',
        'priority': 2
    },
    {
        'keywords': ['tải', 'csv', 'kết', 'quả'],
        'response': 'Trong trang xem kết quả chi tiết của một tác vụ, bạn sẽ thấy nút "Tải xuống CSV" để lưu dữ liệu về máy.',
        'priority': 2
    },
    {
        'keywords': ['xem', 'lỗi', 'task', 'hỏng'],
        'response': 'Nếu tác vụ gặp lỗi (status "Failed"), nút "Xem lỗi" sẽ xuất hiện trong danh sách tác vụ. Nhấn vào đó để xem thông tin chi tiết về lỗi đã xảy ra.',
        'priority': 2
    },
    {
        'keywords': ['trạng', 'thái', 'task', 'nghĩa', 'là', 'gì'],
        'response': 'Các trạng thái của task: Pending (Đang chờ), Running (Đang chạy), Completed (Hoàn thành), Failed (Lỗi), Scheduled (Đã lên lịch và đang chờ đến giờ chạy).',
        'priority': 1
    },
    {
        'keywords': ['cảm', 'ơn', 'thank'],
        'response': 'Rất vui được giúp bạn!',
        'priority': 1
    },
    # Quy tắc mặc định sẽ được xử lý trong hàm nếu không có quy tắc nào khớp
]

# 5.3: Viết hàm get_bot_response(user_input)

def normalize_text(text):
    """Chuẩn hóa text: lowercase, bỏ dấu, bỏ ký tự đặc biệt."""
    # Chuyển thành chữ thường
    text = text.lower()
    # Loại bỏ dấu tiếng Việt
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    # Loại bỏ các ký tự không phải chữ, số, khoảng trắng
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_bot_response(user_input):
    """
    Tìm và trả về câu trả lời phù hợp nhất từ bộ RULES dựa trên user_input.
    """
    normalized_input = normalize_text(user_input)
    matched_rules = []

    if not normalized_input:
        return "Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể diễn đạt lại không?"

    # Tìm tất cả các quy tắc khớp
    for rule in RULES:
        # Chuẩn hóa các từ khóa trong quy tắc (để chắc chắn chúng ở dạng chuẩn)
        normalized_keywords = [normalize_text(kw) for kw in rule['keywords']]
        # Kiểm tra xem ÍT NHẤT MỘT keyword chuẩn hóa có trong input chuẩn hóa không
        any_keyword_found = any(nk in normalized_input for nk in normalized_keywords)
        if any_keyword_found:
            matched_rules.append(rule)

    # Nếu có quy tắc khớp
    if matched_rules:
        # Sắp xếp theo priority giảm dần (cao hơn trước)
        matched_rules.sort(key=lambda r: r.get('priority', 0), reverse=True)
        # Trả về response của quy tắc có priority cao nhất
        return matched_rules[0]['response']
    else:
        # Trả lời mặc định nếu không có quy tắc nào khớp
        return "Xin lỗi, tôi chưa được lập trình để trả lời câu hỏi này. Bạn có thể hỏi về cách tạo task, xem kết quả, lập lịch, hoặc xử lý lỗi không?"

# 5.4: Xây dựng bộ quy tắc ban đầu (đã tích hợp vào RULES ở trên) 