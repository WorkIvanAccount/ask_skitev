# Виртуальное окружение
python -m venv venv
source venv/bin/activate

# Зависимости
pip install -r requirements.txt

# Создание PostgreSQL на ubuntu (Последние три команды отвечают за права)
    sudo -u postgres psql "
    CREATE DATABASE ask_skitev_db;
    \c ask_skitev_db;
    ALTER SCHEMA public OWNER TO postgres;
    GRANT CREATE ON SCHEMA public TO postgres;
    GRANT CREATE ON SCHEMA public TO PUBLIC;
    "

# Миграции
python manage.py migrate
python manage.py migration

# Создание суперпользователя
python manage.py createsuperuser

# Заполнение БД
python manage.py fill_db 10

# Запуск простого WSGI-приложения (Hello World) с 2 воркерами на localhost:8000
gunicorn -w 2 -b 127.0.0.1:8000 gunicorncfg.simple:application

# Запуск Django-приложения с настройками из конфига
gunicorn -c gunicorncfg/config.py ask_skitev.wsgi:application