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
    url = URLField('URL mục tiêu', validators=[DataRequired(message="URL không hợp lệ hoặc bị bỏ trống."), URL(message="Vui lòng nhập URL hợp lệ.")])

    # FieldList cho phép chứa danh sách các form con (SelectorForm)
    # min_entries=1 đảm bảo phải có ít nhất 1 selector được nhập
    selectors = FieldList(FormField(SelectorForm), min_entries=1, label='CSS Selectors')

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
            # Thêm Regexp để kiểm tra định dạng HH:MM (chỉ khi trường này được nhập)
            # Áp dụng validator này nếu schedule_type là 'daily' (logic kiểm tra này nên ở route hoặc service nếu cần chặt chẽ hơn,
            # nhưng thêm ở đây để có phản hồi trên form)
            # -> Cách đơn giản hơn là kiểm tra nếu có giá trị thì phải đúng format HH:MM
            Regexp(r'^([01]\d|2[0-3]):([0-5]\d)$', message='Vui lòng nhập đúng định dạng HH:MM (ví dụ: 09:30 hoặc 23:59).')
        ]
    )

    submit = SubmitField('Lưu tác vụ')

# Form trống chỉ để chứa CSRF token và phục vụ hành động POST an toàn
class DeleteForm(FlaskForm):
    submit = SubmitField('Xóa') # Trường này có thể không dùng trong template nhưng cần để form hợp lệ 