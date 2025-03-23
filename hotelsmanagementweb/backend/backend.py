import json
import mysql.connector
from mysql.connector import Error

# Hàm kết nối MySQL
def connect_to_mysql():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="Hotel_2"
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Hàm đọc file JSON
def read_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None

# Hàm chèn dữ liệu vào MySQL
def insert_data(conn, data):
    try:
        with conn.cursor() as cursor:
            # Chèn dữ liệu khách sạn
            hotels_data = [
                (hotel["hotel_id"], hotel["address_hotel"], hotel["tel"], hotel["hotel_name"], hotel["rating"], hotel["descriptions"])
                for hotel in data["hotels"]
            ]
            cursor.executemany(
                "INSERT INTO hotels (hotel_id, address_hotel, tel, hotel_name, rating, descriptions) VALUES (%s, %s, %s, %s, %s, %s)",
                hotels_data
            )
            conn.commit()

            # Chèn dữ liệu phòng
            rooms_data = []
            for hotel in data["hotels"]:
                for room in hotel["rooms"]:
                    rooms_data.append((
                        room["room_id"], room["room_type"], room["available"], hotel["hotel_id"], room["price"]
                    ))

            cursor.executemany(
                "INSERT INTO rooms (room_id, room_type, available, hotel_id, price) VALUES (%s, %s, %s, %s, %s)",
                rooms_data
            )
            conn.commit()

            # Chèn dữ liệu khách hàng
            # guests_data = [
            #     (guest["guest_id"], guest["guets_name"], guest["email"], guest["phone"], guest["nationality"])
            #     for guest in data["guests"]
            # ]
            # cursor.executemany(
            #     "INSERT INTO guests (guest_id, guets_name, email, phone, nationality) VALUES (%s, %s, %s, %s, %s)",
            #     guests_data
            # )
            # conn.commit()

            # Chèn dữ liệu đặt phòng
            # bookings_data = []
            # for booking in data["bookings"]:
            #     bookings_data.append((
            #         booking["booking_id"], booking["check_in"], booking["check_out"], booking["room_id"], booking["total_price"], booking["guest_id"], booking["payment_status"], booking["create_at"]
            #     ))

            # cursor.executemany(
            #     "INSERT INTO bookings (booking_id, check_in, check_out, room_id, total_price, guest_id, payment_status, create_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            #     bookings_data
            # )
            # conn.commit()

            # Chèn dữ liệu thanh toán
            # payments_data = []
            # for payment in data["payments"]:
            #     payments_data.append((
            #         payment["payment_id"], payment["payment_status"], payment["payment_method"], payment["amount"], payment["guest_id"], payment["booking_id"], payment["create_at"]
            #     ))

            # cursor.executemany(
            #     "INSERT INTO payment (payment_id, payment_status, payment_method, amount, guest_id, booking_id, create_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            #     payments_data
            # )
            # conn.commit()

            # Chèn dữ liệu đánh giá
            reviews_data = []
            for review in data["reviews"]:
                reviews_data.append((
                    review["review_id"], review["guest_id"], review["rating"], review["comment"], review["hotel_id"]
                ))

            cursor.executemany(
                "INSERT INTO reviews (review_id, guest_id, rating, comment, hotel_id) VALUES (%s, %s, %s, %s, %s)",
                reviews_data
            )
            conn.commit()

            # Chèn dữ liệu dịch vụ
            services_data = []
            for service in data["services"]:
                services_data.append((
                    service["id_service"], service["serviceName"], service["room_id"]
                ))

            cursor.executemany(
                "INSERT INTO services (id_service, serviceName, room_id) VALUES (%s, %s, %s)",
                services_data
            )
            conn.commit()

            # Chèn dữ liệu giao dịch
            # transactions_data = []
            # for transaction in data["transactions"]:
            #     transactions_data.append((
            #         transaction["transaction_id"], transaction["payment_id"], transaction["provider_trans"], transaction["respanse_message"], transaction["status_trans"], transaction["created_at"]
            #     ))

            # cursor.executemany(
            #     "INSERT INTO transactions (transaction_id, payment_id, provider_trans, respanse_message, status_trans, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            #     transactions_data
            # )
            # conn.commit()

        print("Data imported successfully!")
    except Error as e:
        print(f"Error inserting data into MySQL: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

# Hàm chính
def main():
    # Kết nối MySQL
    conn = connect_to_mysql()
    if not conn:
        return

    # Đọc file JSON
    data = read_json_file(r"D:\hoc tap\myproject-main\hotelsmanagementweb\database\db.json")
    if not data:
        return

    # Chèn dữ liệu vào MySQL
    insert_data(conn, data)

if __name__ == "__main__":
    main()
