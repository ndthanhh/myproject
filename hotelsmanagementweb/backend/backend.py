import json
import mysql.connector
from mysql.connector import Error

# Hàm kết nối MySQL
def connect_to_mysql():
    try:
        conn = mysql.connector.connect(
            host = "127.0.0.1",
            user = "root",
            password = "",
            database = "Hotel 2"
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
                (hotel["hotelName"], hotel["address"], hotel["rating"])
                for hotel in data["hotels"]
            ]
            cursor.executemany(
                "INSERT INTO hotels (name, location, rating) VALUES (%s, %s, %s)",
                hotels_data
            )
            conn.commit()

            # Lấy ID của các khách sạn vừa chèn
            cursor.execute("SELECT id, name FROM hotels")
            hotels = {name: id for id, name in cursor.fetchall()}

            # Chèn dữ liệu phòng
            rooms_data = []
            for hotel in data["hotels"]:
                hotel_id = hotels[hotel["hotelName"]]
                for room in hotel["rooms"]:
                    rooms_data.append((
                        hotel_id, room["room_number"], room["type"], room["price_per_night"]
                    ))

            cursor.executemany(
                "INSERT INTO rooms (hotel_id, room_number, type, price_per_night) VALUES (%s, %s, %s, %s)",
                rooms_data
            )
            conn.commit()

            # Lấy ID của các phòng vừa chèn
            cursor.execute("SELECT id, hotel_id, room_number FROM rooms")
            rooms = {(hotel_id, room_number): id for id, hotel_id, room_number in cursor.fetchall()}

            # Chèn dữ liệu dịch vụ
            services_data = []
            for hotel in data["hotels"]:
                hotel_id = hotels[hotel["hotelName"]]
                for room in hotel["rooms"]:
                    room_id = rooms[(hotel_id, room["room_number"])]
                    for service in room["services"]:
                        services_data.append((room_id, service))

            cursor.executemany(
                "INSERT INTO services (room_id, service_name) VALUES (%s, %s)",
                services_data
            )
            conn.commit()

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
    data = read_json_file(r"D:\hoc tap\myproject-main\hotelsmanagementweb\databasedb.json")
    if not data:
        return

    # Chèn dữ liệu vào MySQL
    insert_data(conn, data)

if __name__ == "__main__":
    main()
