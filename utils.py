from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Room, Booking, Payment

def create_user(db: Session, username: str, password: str, email: str, full_name: str = None, phone: str = None):
    hashed_password = generate_password_hash(password)
    user = User(
        username=username,
        password=hashed_password,
        email=email,
        full_name=full_name,
        phone=phone
    )
    db.add(user)
    return user

def verify_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def get_available_rooms(db: Session, check_in: datetime, check_out: datetime):
    # Lấy danh sách phòng đã được đặt trong khoảng thời gian
    booked_rooms = db.query(Booking.room_id).filter(
        Booking.check_in_date <= check_out,
        Booking.check_out_date >= check_in,
        Booking.status != 'cancelled'
    ).all()
    booked_room_ids = [room[0] for room in booked_rooms]
    
    # Lấy danh sách phòng còn trống
    available_rooms = db.query(Room).filter(
        Room.is_available == True,
        ~Room.id.in_(booked_room_ids)
    ).all()
    return available_rooms

def create_booking(db: Session, user_id: int, room_id: int, check_in: datetime, check_out: datetime, total_price: float):
    booking = Booking(
        user_id=user_id,
        room_id=room_id,
        check_in_date=check_in,
        check_out_date=check_out,
        total_price=total_price
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def create_payment(db: Session, booking_id: int, amount: float, payment_method: str):
    payment = Payment(
        booking_id=booking_id,
        amount=amount,
        payment_method=payment_method
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment 