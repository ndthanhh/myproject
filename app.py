from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from config import engine, Base, get_db
from sqlalchemy.orm import Session
from functools import wraps
from datetime import datetime, timedelta
from models import User, Room, Booking, Payment
from utils import create_user, verify_user, get_available_rooms, create_booking, create_payment
import re
from werkzeug.security import generate_password_hash
from sqlalchemy import text, inspect

app = Flask(__name__, 
    template_folder='hotelsmanagementweb/pages',
    static_folder='hotelsmanagementweb',
    static_url_path=''
)
app.secret_key = 'your-secret-key-here'  # Thay đổi secret key này trong production
app.permanent_session_lifetime = timedelta(days=7)  # Thời gian lưu session

# Tạo các bảng trong database nếu chưa tồn tại và thêm dữ liệu mẫu nếu cần
def init_db():
    try:
        inspector = inspect(engine)
        
        # Kiểm tra xem bảng rooms có tồn tại và có đúng cấu trúc không
        if 'rooms' in inspector.get_table_names():
            columns = {column['name']: column for column in inspector.get_columns('rooms')}
            required_columns = ['room_number', 'room_type', 'price', 'description', 'capacity', 'is_available']
            
            # Kiểm tra xem có thiếu cột nào không
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                print(f"Bảng rooms thiếu các cột: {missing_columns}")
                # Xóa các bảng theo thứ tự để tránh lỗi khóa ngoại
                with engine.begin() as conn:
                    conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
                    conn.execute(text("DROP TABLE IF EXISTS payments"))
                    conn.execute(text("DROP TABLE IF EXISTS bookings"))
                    conn.execute(text("DROP TABLE IF EXISTS rooms"))
                    conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
                print("Đã xóa và sẽ tạo lại các bảng với cấu trúc mới")
        
        # Tạo các bảng nếu chưa tồn tại hoặc đã bị xóa do cấu trúc sai
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        # Kiểm tra và thêm dữ liệu mẫu nếu cần
        db = next(get_db())
        
        try:
            # Kiểm tra xem đã có admin chưa
            admin = db.query(User).filter(User.is_admin == True).first()
            if not admin:
                # Tạo tài khoản admin
                admin = User(
                    username="admin",
                    password=generate_password_hash("Admin123"),
                    email="admin@example.com",
                    full_name="Administrator",
                    is_admin=True
                )
                db.add(admin)
                db.commit()
                print("Đã tạo tài khoản admin!")
            
            # Kiểm tra xem đã có phòng nào chưa
            rooms_count = db.query(Room).count()
            if rooms_count == 0:
                # Tạo các phòng mẫu
                rooms = [
                    Room(
                        room_number="101",
                        room_type="Standard",
                        price=500000,
                        description="Phòng tiêu chuẩn với đầy đủ tiện nghi cơ bản",
                        capacity=2,
                        is_available=True
                    ),
                    Room(
                        room_number="102",
                        room_type="Deluxe",
                        price=800000,
                        description="Phòng cao cấp với view đẹp",
                        capacity=3,
                        is_available=True
                    ),
                    Room(
                        room_number="103",
                        room_type="Suite",
                        price=1200000,
                        description="Phòng suite sang trọng",
                        capacity=4,
                        is_available=True
                    )
                ]
                for room in rooms:
                    db.add(room)
                db.commit()
                print("Đã tạo các phòng mẫu!")
            
            print("Đã kiểm tra và khởi tạo database thành công!")
            
        except Exception as e:
            db.rollback()
            print(f"Lỗi khi thêm dữ liệu mẫu: {str(e)}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"Lỗi khi khởi tạo database: {str(e)}")

# Khởi tạo database khi chạy ứng dụng
init_db()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để truy cập trang này!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để truy cập trang này!', 'error')
            return redirect(url_for('login'))
        db = next(get_db())
        user = db.query(User).filter(User.id == session['user_id']).first()
        if not user or not user.is_admin:
            flash('Bạn không có quyền truy cập trang này!', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Validation functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    if not phone:
        return True  # Phone is optional
    pattern = r'^\+?[0-9]{10,15}$'
    return re.match(pattern, phone) is not None

def validate_password(password):
    # At least 8 characters, must contain both letters and numbers
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):  # Kiểm tra có chữ
        return False
    if not re.search(r'[0-9]', password):  # Kiểm tra có số
        return False
    return True

# Routes
@app.route('/')
def home():
    db = next(get_db())
    rooms = db.query(Room).filter(Room.is_available == True).all()
    return render_template('home.html', rooms=rooms)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Nếu người dùng đã đăng nhập, chuyển hướng đến trang chủ
    if 'user_id' in session:
        return jsonify({'success': False, 'message': 'Bạn đã đăng nhập!'})
        
    if request.method == 'POST':
        # Lấy dữ liệu JSON từ request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember', False)
        
        # Validation
        if not username or not password:
            return jsonify({'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin!'})
        
        db = next(get_db())
        user = verify_user(db, username, password)
        
        if user:
            # Lưu thông tin người dùng vào session
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            # Nếu người dùng chọn "Nhớ mật khẩu", đặt session permanent
            if remember:
                session.permanent = True
                
            return jsonify({
                'success': True, 
                'message': 'Đăng nhập thành công!',
                'redirect': url_for('home')
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Tên đăng nhập hoặc mật khẩu không đúng!'
            })
    
    # Nếu là GET request, hiển thị trang đăng nhập/đăng ký
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Lấy dữ liệu JSON từ request
            data = request.get_json()
            if not data:
                data = request.form  # Thử lấy form data nếu không có JSON
            
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            full_name = data.get('full_name')
            phone = data.get('phone')
            
            # Validation
            if not username or not password or not email:
                return jsonify({'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin bắt buộc!'})
            
            if not validate_email(email):
                return jsonify({'success': False, 'message': 'Email không hợp lệ!'})
            
            if not validate_password(password):
                return jsonify({'success': False, 'message': 'Mật khẩu phải có ít nhất 8 ký tự, bao gồm cả chữ và số!'})
            
            if phone and not validate_phone(phone):
                return jsonify({'success': False, 'message': 'Số điện thoại không hợp lệ!'})
            
            db = next(get_db())
            
            # Check if username already exists
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                return jsonify({'success': False, 'message': 'Tên đăng nhập đã tồn tại!'})
            
            # Check if email already exists
            existing_email = db.query(User).filter(User.email == email).first()
            if existing_email:
                return jsonify({'success': False, 'message': 'Email đã được sử dụng!'})
            
            # Create new user using the create_user function
            user = create_user(db, username, password, email, full_name, phone)
            
            # Commit changes to database
            db.commit()
            
            return jsonify({'success': True, 'message': 'Đăng ký thành công! Vui lòng đăng nhập.'})
            
        except Exception as e:
            if db:
                db.rollback()  # Rollback changes if there's an error
            print(f"Error during registration: {str(e)}")  # Print error for debugging
            return jsonify({'success': False, 'message': f'Đăng ký thất bại! Lỗi: {str(e)}'})
        finally:
            if db:
                db.close()  # Close database connection
    
    # Nếu là GET request, hiển thị trang đăng nhập/đăng ký
    return render_template('register.html')

@app.route('/user')
@login_required
def user():
    db = next(get_db())
    user = db.query(User).filter(User.id == session['user_id']).first()
    bookings = db.query(Booking).filter(Booking.user_id == user.id).all()
    return render_template('user.html', user=user, bookings=bookings)

@app.route('/detailroom/<int:room_id>')
def detailroom(room_id):
    db = next(get_db())
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        flash('Không tìm thấy phòng!', 'error')
        return redirect(url_for('home'))
    return render_template('detailroom.html', room=room)

@app.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        check_in_str = request.form.get('check_in')
        check_out_str = request.form.get('check_out')
        
        # Validation
        if not room_id or not check_in_str or not check_out_str:
            flash('Vui lòng nhập đầy đủ thông tin!', 'error')
            return redirect(url_for('detailroom', room_id=room_id))
        
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d')
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d')
        except ValueError:
            flash('Ngày không hợp lệ!', 'error')
            return redirect(url_for('detailroom', room_id=room_id))
        
        # Check if check-in date is in the future
        if check_in < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            flash('Ngày check-in phải là ngày trong tương lai!', 'error')
            return redirect(url_for('detailroom', room_id=room_id))
        
        # Check if check-out date is after check-in date
        if check_out <= check_in:
            flash('Ngày check-out phải sau ngày check-in!', 'error')
            return redirect(url_for('detailroom', room_id=room_id))
        
        db = next(get_db())
        room = db.query(Room).filter(Room.id == room_id).first()
        
        if not room:
            flash('Không tìm thấy phòng!', 'error')
            return redirect(url_for('home'))
        
        # Check if room is available for the selected dates
        existing_bookings = db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.check_in_date <= check_out,
            Booking.check_out_date >= check_in,
            Booking.status != 'cancelled'
        ).all()
        
        if existing_bookings:
            flash('Phòng đã được đặt trong khoảng thời gian này!', 'error')
            return redirect(url_for('detailroom', room_id=room_id))
            
        # Tính tổng tiền
        days = (check_out - check_in).days
        total_price = room.price * days
        
        # Tạo booking
        booking = create_booking(db, session['user_id'], room_id, check_in, check_out, total_price)
        
        session['booking_id'] = booking.id
        return redirect(url_for('payment'))
        
    room_id = request.args.get('room_id')
    if not room_id:
        return redirect(url_for('home'))
        
    db = next(get_db())
    room = db.query(Room).filter(Room.id == room_id).first()
    return render_template('booking.html', room=room)

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if 'booking_id' not in session:
        return redirect(url_for('home'))
        
    db = next(get_db())
    booking = db.query(Booking).filter(Booking.id == session['booking_id']).first()
    
    if not booking:
        flash('Không tìm thấy thông tin đặt phòng!', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if not payment_method:
            flash('Vui lòng chọn phương thức thanh toán!', 'error')
            return render_template('payment.html', booking=booking)
        
        # Tạo payment
        payment = create_payment(db, booking.id, booking.total_price, payment_method)
        
        # Cập nhật trạng thái booking
        booking.status = 'confirmed'
        db.commit()
        
        session.pop('booking_id', None)
        flash('Thanh toán thành công!', 'success')
        return redirect(url_for('success'))
        
    return render_template('payment.html', booking=booking)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất!', 'success')
    return redirect(url_for('home'))

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    db = next(get_db())
    rooms = db.query(Room).all()
    bookings = db.query(Booking).all()
    users = db.query(User).all()
    return render_template('admin/dashboard.html', rooms=rooms, bookings=bookings, users=users)

@app.route('/admin/rooms', methods=['GET', 'POST'])
@admin_required
def admin_rooms():
    db = next(get_db())
    if request.method == 'POST':
        room_number = request.form.get('room_number')
        room_type = request.form.get('room_type')
        price_str = request.form.get('price')
        description = request.form.get('description')
        capacity_str = request.form.get('capacity')
        
        # Validation
        if not room_number or not room_type or not price_str or not capacity_str:
            flash('Vui lòng nhập đầy đủ thông tin!', 'error')
            return redirect(url_for('admin_rooms'))
        
        try:
            price = float(price_str)
            capacity = int(capacity_str)
        except ValueError:
            flash('Giá phòng và sức chứa phải là số!', 'error')
            return redirect(url_for('admin_rooms'))
        
        if price <= 0:
            flash('Giá phòng phải lớn hơn 0!', 'error')
            return redirect(url_for('admin_rooms'))
        
        if capacity <= 0:
            flash('Sức chứa phải lớn hơn 0!', 'error')
            return redirect(url_for('admin_rooms'))
        
        # Check if room number already exists
        existing_room = db.query(Room).filter(Room.room_number == room_number).first()
        if existing_room:
            flash('Số phòng đã tồn tại!', 'error')
            return redirect(url_for('admin_rooms'))
        
        room = Room(
            room_number=room_number,
            room_type=room_type,
            price=price,
            description=description,
            capacity=capacity
        )
        db.add(room)
        db.commit()
        flash('Thêm phòng thành công!', 'success')
        return redirect(url_for('admin_rooms'))
        
    rooms = db.query(Room).all()
    return render_template('admin/rooms.html', rooms=rooms)

@app.route('/admin/rooms/<int:room_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_room(room_id):
    db = next(get_db())
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        flash('Không tìm thấy phòng!', 'error')
        return redirect(url_for('admin_rooms'))
    
    if request.method == 'POST':
        room_number = request.form.get('room_number')
        room_type = request.form.get('room_type')
        price_str = request.form.get('price')
        description = request.form.get('description')
        capacity_str = request.form.get('capacity')
        
        # Validation
        if not room_number or not room_type or not price_str or not capacity_str:
            flash('Vui lòng nhập đầy đủ thông tin!', 'error')
            return render_template('admin/edit_room.html', room=room)
        
        try:
            price = float(price_str)
            capacity = int(capacity_str)
        except ValueError:
            flash('Giá phòng và sức chứa phải là số!', 'error')
            return render_template('admin/edit_room.html', room=room)
        
        if price <= 0:
            flash('Giá phòng phải lớn hơn 0!', 'error')
            return render_template('admin/edit_room.html', room=room)
        
        if capacity <= 0:
            flash('Sức chứa phải lớn hơn 0!', 'error')
            return render_template('admin/edit_room.html', room=room)
        
        # Check if room number already exists (if changed)
        if room_number != room.room_number:
            existing_room = db.query(Room).filter(Room.room_number == room_number).first()
            if existing_room:
                flash('Số phòng đã tồn tại!', 'error')
                return render_template('admin/edit_room.html', room=room)
        
        room.room_number = room_number
        room.room_type = room_type
        room.price = price
        room.description = description
        room.capacity = capacity
        room.is_available = request.form.get('is_available') == 'on'
        
        db.commit()
        flash('Cập nhật phòng thành công!', 'success')
        return redirect(url_for('admin_rooms'))
        
    return render_template('admin/edit_room.html', room=room)

@app.route('/admin/rooms/<int:room_id>/delete', methods=['POST'])
@admin_required
def admin_delete_room(room_id):
    db = next(get_db())
    room = db.query(Room).filter(Room.id == room_id).first()
    
    if not room:
        flash('Không tìm thấy phòng!', 'error')
        return redirect(url_for('admin_rooms'))
    
    # Check if room has any bookings
    bookings = db.query(Booking).filter(Booking.room_id == room_id).all()
    if bookings:
        flash('Không thể xóa phòng đã có đặt phòng!', 'error')
        return redirect(url_for('admin_rooms'))
    
    db.delete(room)
    db.commit()
    flash('Xóa phòng thành công!', 'success')
    return redirect(url_for('admin_rooms'))

if __name__ == '__main__':
    app.run(debug=True) 