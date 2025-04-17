from datetime import datetime, timezone, timedelta

def to_local_time(utc_dt):
    """Chuyển đổi datetime UTC sang giờ địa phương Việt Nam (UTC+7)."""
    if utc_dt is None:
        return None
    # Đảm bảo datetime nhận vào là timezone-aware UTC
    if utc_dt.tzinfo is None:
        # Nếu là naive, giả định nó là UTC (cần xem lại logic lưu trữ nếu khác)
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    else:
        # Nếu đã có timezone, chuyển về UTC trước khi chuyển sang +7
        utc_dt = utc_dt.astimezone(timezone.utc)

    # Tạo timezone UTC+7
    local_tz = timezone(timedelta(hours=7))
    return utc_dt.astimezone(local_tz)

def format_datetime(value, fmt='%d/%m/%Y %H:%M'):
    """Định dạng datetime object thành chuỗi với format cụ thể."""
    if value is None:
        return "-" # Hoặc trả về chuỗi rỗng '' tùy ý
    try:
        return value.strftime(fmt)
    except AttributeError:
        # Trả về giá trị gốc nếu không phải là datetime object hợp lệ
        return value 