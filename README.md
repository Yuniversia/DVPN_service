# DVPN Service

## English

### Project Description
A decentralized VPN service built with Python/Flask that provides peer-to-peer connection management with optional encryption support.

### Features
- User registration/authentication
- Peer connection management
- Token-based API access
- Optional encryption support

### Requirements
- Python 3.7+
- Packages (see `requirements.txt`):
  - Flask
  - Flask-WTF
  - Flask-Login
  - Flask-SQLAlchemy

### Installation
```bash
git clone [your-repository-url]
cd dvpn-service
pip install -r requirements.txt
```

### Configuration
1. Rename `.env.example` to `.env`
2. Update environment variables:
```env
SECRET_KEY=your_secret_key_here
SQLALCHEMY_DATABASE_URI=sqlite:///db.sqlite3  # or other DB connection
```

### Running the Service
```bash
python run.py
```
Server starts at `http://127.0.0.1:5000`

### API Usage

#### Get Peer List
**Endpoint**: `POST /peers`

**Request**:
```json
{
  "token": "your_generated_token"
}
```

**Response Example**:
```json
[
  {
    "name": "user_1",
    "addr": "192.168.0.1",
    "id": "a1b2c3d4-e5f6-7890-g1h2-ijklmnopqrst",
    "crypto": {
      "key": "9z8y7x6w5v4u3t2s1r0q"
    }
  },
  {
    "name": "user_2",
    "addr": "192.168.0.2",
    "id": "b2c3d4e5-f6g7-8901-h2i3-jklmnopqrstu"
  }
]
```

### Notes
- Users with enabled encryption will have `crypto` field
- Main application logic after registration: `domain/person`

---

## Русский

### Описание проекта
Децентрализованный VPN-сервис на Python/Flask для управления пиринговыми подключениями с опциональной поддержкой шифрования.

### Основные функции
- Регистрация/аутентификация пользователей
- Управление пиринговыми подключениями
- API с токен-авторизацией
- Опциональное шифрование соединений

### Требования
- Python 3.7+
- Пакеты (см. `requirements.txt`):
  - Flask
  - Flask-WTF
  - Flask-Login
  - Flask-SQLAlchemy

### Установка
```bash
git clone [your-repository-url]
cd dvpn-service
pip install -r requirements.txt
```

### Настройка
1. Переименуйте `.env.example` в `.env`
2. Задайте параметры:
```env
SECRET_KEY=ваш_секретный_ключ
SQLALCHEMY_DATABASE_URI=sqlite:///db.sqlite3  # или другая СУБД
```

### Запуск сервиса
```bash
python run.py
```
Сервер запустится по адресу `http://127.0.0.1:5000`

### Использование API

#### Получение списка пиров
**Эндпоинт**: `POST /peers`

**Запрос**:
```json
{
  "token": "ваш_сгенерированный_токен"
}
```

**Пример ответа**:
```json
[
  {
    "name": "user_1",
    "addr": "192.168.0.1",
    "id": "a1b2c3d4-e5f6-7890-g1h2-ijklmnopqrst",
    "crypto": {
      "key": "9z8y7x6w5v4u3t2s1r0q"
    }
  },
  {
    "name": "user_2",
    "addr": "192.168.0.2",
    "id": "b2c3d4e5-f6g7-8901-h2i3-jklmnopqrstu"
  }
]
```

### Примечания
- Пользователи с включенным шифрованием содержат поле `crypto`
- Основная логика приложения после регистрации: `domain/person`