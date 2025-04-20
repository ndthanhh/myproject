import os
import mysql.connector

# Kết nối database
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="170705",
    database="btl_csdl"
)
cursor = conn.cursor()

# Thư mục gốc chứa ảnh
base_path = "D:/Newfolder/myproject/myproject-main/hotelsmanagementweb/assets/10"

hotel_id = 10  # ví dụ ID khách sạn là 10

# Lưu ảnh khách sạn chung
for file in os.listdir(base_path):
    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        image_path = os.path.join(base_path, file).replace("\\", "/")
        cursor.execute("INSERT INTO hotel_images (hotel_id, image_path) VALUES (%s, %s)", (hotel_id, image_path))

# Lưu ảnh các loại phòng (folder 1, 2, 3)
for folder_name in ['28', '29', '30']:
    room_id = int(folder_name)  # giả sử folder 1 tương ứng room_id = 1
    folder_path = os.path.join(base_path, folder_name)
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            image_path = os.path.join(folder_path, file).replace("\\", "/")
            cursor.execute("INSERT INTO room_images (room_id, image_path) VALUES (%s, %s)", (room_id, image_path))

conn.commit()
cursor.close()
conn.close()
print("Đã lưu toàn bộ ảnh thành công vào database!")
