from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from config import engine, Base, get_db
from sqlalchemy.orm import Session
from functools import wraps
from datetime import datetime, timedelta
from models import User, Hotel, Room, Service, Review, Booking, Payment
from utils import (
    create_user, verify_user, get_available_rooms, create_booking, 
    create_payment, create_review, get_hotel_by_id, get_room_by_id, 
    get_user_by_id, get_booking_by_id, get_user_bookings, get_hotel_reviews
)
import re
from sqlalchemy import text, inspect

app = Flask(__name__, 
    template_folder='hotelsmanagementweb/pages',
    static_folder='hotelsmanagementweb',
    static_url_path=''
)
app.secret_key = 'your-secret-key-here'  # Thay đổi secret key này trong production
app.permanent_session_lifetime = timedelta(days=7)  # Thời gian lưu session

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để truy cập trang này!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route cho trang chủ
@app.route('/')
def index():
    db = next(get_db())
    hotels = db.query(Hotel).all()
    return render_template('home.html', hotels=hotels)

# Route cho đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not all([username, password]):
            flash('Vui lòng điền đầy đủ thông tin đăng nhập', 'error')
            return redirect(url_for('login'))
            
        db = next(get_db())
        user = verify_user(db, username, password)
        
        if user:
            session['user_id'] = user.user_id
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'error')
            return redirect(url_for('login'))
            
    return render_template('login.html')

# Route cho đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        if not all([username, password, email]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc', 'error')
            return redirect(url_for('register'))
            
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Email không hợp lệ', 'error')
            return redirect(url_for('register'))
            
        db = next(get_db())
        try:
            user = create_user(db, username, password, email, full_name, phone)
            session['user_id'] = user.user_id
            flash('Đăng ký thành công!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.rollback()
            print(f"Error during registration: {str(e)}")  # Thêm log chi tiết
            flash(f'Có lỗi xảy ra khi đăng ký: {str(e)}', 'error')
            return redirect(url_for('register'))
            
    return render_template('register.html')

# Route cho đặt phòng
@app.route('/book/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    db = next(get_db())
    room = get_room_by_id(db, room_id)
    if not room:
        flash('Không tìm thấy phòng', 'error')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        check_in = datetime.strptime(request.form.get('check_in'), '%Y-%m-%d')
        check_out = datetime.strptime(request.form.get('check_out'), '%Y-%m-%d')
        
        if check_in >= check_out:
            flash('Ngày check-out phải sau ngày check-in', 'error')
            return redirect(url_for('book_room', room_id=room_id))
            
        # Tính tổng giá
        nights = (check_out - check_in).days
        total_price = room.price * nights
        
        try:
            # Tạo booking
            booking = create_booking(
                db,
                session['user_id'],
                room_id,
                check_in,
                check_out,
                total_price
            )
            
            # Tạo payment
            payment = create_payment(
                db,
                booking.booking_id,
                total_price,
                'pending',
                session['user_id']
            )
            
            # Cập nhật số lượng phòng trống
            room.availableRooms -= 1
            db.commit()
            
            flash('Đặt phòng thành công!', 'success')
            return redirect(url_for('booking_details', booking_id=booking.booking_id))
            
        except Exception as e:
            db.rollback()
            flash('Có lỗi xảy ra khi đặt phòng', 'error')
            return redirect(url_for('book_room', room_id=room_id))
            
    return render_template('book_room.html', room=room)

# Route cho xem chi tiết đặt phòng
@app.route('/booking/<int:booking_id>')
@login_required
def booking_details(booking_id):
    db = next(get_db())
    booking = get_booking_by_id(db, booking_id)
    if not booking or booking.user_id != session['user_id']:
        flash('Không tìm thấy thông tin đặt phòng', 'error')
        return redirect(url_for('index'))
        
    return render_template('booking_details.html', booking=booking)

# Route cho xem lịch sử đặt phòng
@app.route('/my-bookings')
@login_required
def my_bookings():
    db = next(get_db())
    bookings = get_user_bookings(db, session['user_id'])
    return render_template('my_bookings.html', bookings=bookings)

# Route cho đánh giá khách sạn
@app.route('/hotel/<int:hotel_id>/review', methods=['POST'])
@login_required
def review_hotel(hotel_id):
    rating = float(request.form.get('rating'))
    comment = request.form.get('comment')
    
    if not rating or rating < 0 or rating > 5:
        flash('Đánh giá không hợp lệ', 'error')
        return redirect(url_for('hotel_details', hotel_id=hotel_id))
        
    db = next(get_db())
    try:
        review = create_review(db, session['user_id'], hotel_id, rating, comment)
        flash('Đánh giá thành công!', 'success')
    except Exception as e:
        db.rollback()
        flash('Có lỗi xảy ra khi đánh giá', 'error')
        
    return redirect(url_for('hotel_details', hotel_id=hotel_id))

# Route cho xem chi tiết khách sạn
@app.route('/hotel/<int:hotel_id>')
def hotel_details(hotel_id):
    db = next(get_db())
    hotel = get_hotel_by_id(db, hotel_id)
    if not hotel:
        flash('Không tìm thấy khách sạn', 'error')
        return redirect(url_for('index'))
        
    reviews = get_hotel_reviews(db, hotel_id)
    return render_template('hotel_details.html', hotel=hotel, reviews=reviews)

# Route cho đăng xuất
@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất thành công!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    try:
        # Tạo database và bảng
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        
    app.run(debug=True) 