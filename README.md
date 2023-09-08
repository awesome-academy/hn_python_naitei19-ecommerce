# hn_python_naitei19-ecommerce
Project thực hiện trong quá trình training hè tại Sun*

## Cách cài đặt
Các bước cài đặt:
1. Clone/pull/download repository này về
2. Chạy lệnh sau để khởi tạo virtual ennvironment:
```
virtualenv venv
source venv/bin/activate
```
3. Cài đặt các thư viện:
```
pip install -r requirements.txt
```
4. Copy file `.env.example` ra 1 file mới, đặt tên là `.env` và sửa các giá trị
5. Khởi tạo database:
```commandline
python3 manage.py makemigrations
python3 manage.py migrate
```
6. Khởi động server:
```commandline
python3 manage.py runserver
```
