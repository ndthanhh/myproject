CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(255),
    email VARCHAR(100),
    full_name VARCHAR(100),
    phone VARCHAR(20),
    is_admin TINYINT(1)
);

CREATE TABLE hotels (
    hotel_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_name VARCHAR(50),
    address_hotel VARCHAR(150),
    tel VARCHAR(13),
    rating FLOAT,
    descriptions VARCHAR(1000)
);

CREATE TABLE rooms (
    room_id INT PRIMARY KEY,
    room_type VARCHAR(35),
    availableRooms INT,
    price BIGINT,
    hotel_id INT,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)
);

CREATE TABLE services (
    id_service INT PRIMARY KEY,
    serviceName VARCHAR(255),
    room_id INT,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    room_id INT,
    check_in DATETIME,
    check_out DATETIME,
    total_price FLOAT,
    status VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

CREATE TABLE payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_status VARCHAR(10),
    payment_method ENUM('vnpay', 'momo'),
    amount BIGINT,
    user_id INT,
    booking_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

CREATE TABLE reviews (
    review_id INT PRIMARY KEY,
    user_id INT,
    rating FLOAT,
    comment VARCHAR(200),
    hotel_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)
);
