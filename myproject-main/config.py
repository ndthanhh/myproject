from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Thông tin kết nối MySQL
MYSQL_USER = "root"
MYSQL_PASSWORD = "170705"
MYSQL_HOST = "127.0.0.1"  # Sử dụng 127.0.0.1 thay vì localhost
MYSQL_PORT = "3306"
MYSQL_DB = "btl_csdl"

# Tạo URL kết nối với các tham số bổ sung
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"

# Tạo engine với các tham số bổ sung
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Kiểm tra kết nối trước khi sử dụng
    pool_recycle=3600,   # Tái sử dụng kết nối sau 1 giờ
    echo=True           # Hiển thị SQL queries để debug
)

# Tạo SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo Base class
Base = declarative_base()

# Dependency để lấy DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
