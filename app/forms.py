from flask_wtf import FlaskForm
from wtforms import StringField, URLField, FieldList, FormField, SelectField, SubmitField
from wtforms.validators import DataRequired, URL, Optional, Length, Regexp

class SelectorForm(FlaskForm):
    """Form con để nhập một cặp Tên dữ liệu và CSS Selector."""
    # Không cần kế thừa FlaskForm ở đây vì nó được dùng như FormField
    # Tuy nhiên, để dễ test hoặc tái sử dụng độc lập thì có thể giữ lại
    data_name = StringField('Tên dữ liệu', validators=[DataRequired(message="Tên dữ liệu không được để trống."), Length(max=100)])
    css_selector = StringField('CSS Selector', validators=[DataRequired(message="CSS Selector không được để trống."), Length(max=500)])
    # Bỏ SubmitField ở đây vì nó là form con

class TaskForm(FlaskForm):
    """Form chính để tạo hoặc chỉnh sửa một Task scraping."""
    name = StringField('Tên tác vụ', validators=[DataRequired(message="Tên tác vụ không được để trống."), Length(max=128)])
    url = URLField('URL mục tiêu', validators=[DataRequired(message="URL không được để trống."), URL(message="Vui lòng nhập URL hợp lệ (ví dụ: http://example.com).")])

    # FieldList cho phép chứa danh sách các form con (SelectorForm)
    # min_entries=1 đảm bảo phải có ít nhất 1 selector được nhập
    selectors = FieldList(FormField(SelectorForm), min_entries=1, label='CSS Selectors', validators=[DataRequired(message="Phải có ít nhất một selector được cấu hình.")])

    # Các lựa chọn cho lập lịch
    schedule_type = SelectField(
        'Loại lập lịch',
        choices=[
            ('none', 'Không lập lịch'),
            ('interval', 'Chạy định kỳ theo Phút (Interval)'),
            ('daily', 'Chạy hàng ngày vào lúc (HH:MM)')
        ],
        default='none',
        validators=[Optional()]
    )
    # Trường này sẽ được hiển thị/ẩn bằng JavaScript tùy thuộc vào schedule_type
    # Ví dụ: Nếu 'interval', nhập số phút. Nếu 'daily', nhập giờ:phút.
    schedule_value = StringField(
        'Giá trị lập lịch',
        validators=[
            Optional(), # Vẫn là Optional vì không phải lúc nào cũng cần
            Length(max=128),
            # Thêm Regexp để kiểm tra định dạng HH:MM khi schedule_type là 'daily'
            # Logic kiểm tra điều kiện sẽ nằm trong JavaScript và route/service
            # Ở đây chỉ kiểm tra format cơ bản nếu có giá trị
            # Regexp(r'^(\d+)|([01]\d|2[0-3]):([0-5]\d)$', message='Định dạng không hợp lệ. Nhập số phút cho Interval hoặc HH:MM cho Daily.')
            # Bỏ Regexp phức tạp ở đây, sẽ validate ở route/service dựa trên type
        ]
    )

    submit = SubmitField('Lưu tác vụ')

# Form trống chỉ để chứa CSRF token và phục vụ hành động POST an toàn
class DeleteForm(FlaskForm):
    submit = SubmitField('Xóa') # Trường này có thể không dùng trong template nhưng cần để form hợp lệ 