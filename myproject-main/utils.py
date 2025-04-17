from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Hotel, Room, Service, Review, Booking, Payment

def create_user(db: Session, username: str, password: str, email: str, full_name: str = None, phone: str = None):
    hashed_password = generate_password_hash(password)
    user = User(
        username=username,
        password=hashed_password,
        email=email,
        full_name=full_name,
        phone=phone,
        is_admin=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def create_guest(db: Session, guest_name: str, email: str, phone: str, nationality: str = None):
    guest = Guest(
        guest_name=guest_name,
        email=email,
        phone=phone,
        nationality=nationality
    )
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest

def get_available_rooms(db: Session, hotel_id: int = None, room_type: str = None):
    query = db.query(Room).filter(Room.availableRooms > 0)
    
    if hotel_id:
        query = query.filter(Room.hotel_id == hotel_id)
    if room_type:
        query = query.filter(Room.room_type == room_type)
        
    return query.all()

def create_booking(db: Session, user_id: int, room_id: int, check_in: datetime, check_out: datetime, total_price: float):
    booking = Booking(
        user_id=user_id,
        room_id=room_id,
        check_in=check_in,
        check_out=check_out,
        total_price=total_price,
        status='pending'
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def create_payment(db: Session, booking_id: int, amount: int, payment_method: str, user_id: int):
    payment = Payment(
        booking_id=booking_id,
        amount=amount,
        payment_method=payment_method,
        payment_status='pending',
        user_id=user_id
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def create_review(db: Session, user_id: int, hotel_id: int, rating: float, comment: str):
    review = Review(
        user_id=user_id,
        hotel_id=hotel_id,
        rating=rating,
        comment=comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

def get_hotel_by_id(db: Session, hotel_id: int):
    return db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()

def get_room_by_id(db: Session, room_id: int):
    return db.query(Room).filter(Room.room_id == room_id).first()

def get_guest_by_id(db: Session, guest_id: int):
    return db.query(Guest).filter(Guest.id == guest_id).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()

def get_booking_by_id(db: Session, booking_id: int):
    return db.query(Booking).filter(Booking.booking_id == booking_id).first()

def get_user_bookings(db: Session, user_id: int):
    return db.query(Booking).filter(Booking.user_id == user_id).all()

def get_hotel_reviews(db: Session, hotel_id: int):
    return db.query(Review).filter(Review.hotel_id == hotel_id).all() 