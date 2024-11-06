Bước 1: Sau khi clone git theo url
Bước 2: Điều chỉnh database theo cấu hình MySQL trên máy tính của cá nhân
DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': '<your_namedb>',
        'USER': 'root',
        'PASSWORD': '<your_pw>',
        'HOST': '127.0.0.1',
        'PORT': '<your_port>',
    }
}

Bước 3: Chạy câu lệnh :
python manage.py makemigrations
python manage.py migrate
Bước 4: Chạy server:
python manage.py runserver

Bước 5: done!!
