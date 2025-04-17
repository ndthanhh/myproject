from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from config import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    is_admin = Column(Integer, default=0)  # tinyint(1)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class Hotel(Base):
    __tablename__ = 'hotels'
    
    hotel_id = Column(Integer, primary_key=True, autoincrement=True)
    hotel_name = Column(String(50), nullable=False)
    address_hotel = Column(String(150), nullable=False)
    tel = Column(String(20), nullable=False)
    rating = Column(Float)
    descriptions = Column(String(1000))
    
    # Relationships
    rooms = relationship("Room", back_populates="hotel")
    reviews = relationship("Review", back_populates="hotel")

class Room(Base):
    __tablename__ = 'rooms'
    
    room_id = Column(Integer, primary_key=True, autoincrement=True)
    room_type = Column(String(25), nullable=False)
    availableRooms = Column(Integer)
    price = Column(Integer, nullable=False)
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'), nullable=False)
    
    # Relationships
    hotel = relationship("Hotel", back_populates="rooms")
    services = relationship("Service", back_populates="room")
    bookings = relationship("Booking", back_populates="room")

class Service(Base):
    __tablename__ = 'services'
    
    id_service = Column(Integer, primary_key=True, autoincrement=True)
    serviceName = Column(String(255), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.room_id'), nullable=False)
    
    # Relationships
    room = relationship("Room", back_populates="services")

class Review(Base):
    __tablename__ = 'reviews'
    
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    rating = Column(Float)
    comment = Column(String(200))
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    hotel = relationship("Hotel", back_populates="reviews")

class Booking(Base):
    __tablename__ = 'bookings'
    
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.room_id'), nullable=False)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(20), default='pending')
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)

class Payment(Base):
    __tablename__ = 'payment'
    
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    payment_status = Column(String(10))
    payment_method = Column(Enum('vnpay', 'momo'), nullable=False)
    amount = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    booking_id = Column(Integer, ForeignKey('bookings.booking_id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    booking = relationship("Booking", back_populates="payment") 