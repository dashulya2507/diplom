# Backend-приложение для автоматизации закупок

Дипломный проект Netology «Python-разработчик: расширенный курс».

## Стек

- Python 3.10+
- Django 5
- Django REST Framework
- SQLite для локального запуска
- PostgreSQL можно подключить через настройки проекта
- Celery + Redis для продвинутой части
- PyYAML для импорта прайсов
- requests для загрузки прайсов по URL

## Возможности

- регистрация покупателя;
- подтверждение email;
- авторизация по email и токену DRF;
- просмотр каталога товаров;
- поиск и фильтрация по поставщику и категории;
- просмотр характеристик товара;
- корзина;
- контакты/адреса доставки;
- оформление заказа с товарами разных поставщиков;
- история и детали заказов;
- изменение статуса заказа администратором;
- email-уведомления;
- импорт товаров из YAML;
- запуск импорта из Django Admin;
- Celery-задачи для импорта и email;
- API поставщика: обновление прайса, управление приёмом заказов и просмотр заказов.

## Установка

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

## Запуск локально

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py import_products
python manage.py runserver
```

При стандартных настройках Celery работает в eager-режиме, поэтому для локальной проверки Redis не нужен.

API будет доступно по адресу `http://127.0.0.1:8000/api/`.

Админка: `http://127.0.0.1:8000/admin/`.

## Основные endpoint'ы

- `POST /api/register/` — регистрация
- `POST /api/register/confirm/` — подтверждение email
- `POST /api/login/` — авторизация
- `GET /api/me/` — текущий пользователь
- `GET /api/categories/` — категории
- `GET /api/shops/` — поставщики
- `GET /api/products/` — каталог
- `GET /api/products/<id>/` — товар
- `GET /api/product-info/<id>/` — предложение поставщика
- `GET/POST /api/contacts/` — контакты
- `DELETE /api/contacts/<id>/` — удалить контакт
- `GET /api/cart/` — корзина
- `POST /api/cart/add/` — добавить товар
- `DELETE /api/cart/<id>/` — удалить позицию
- `GET /api/orders/` — заказы пользователя
- `POST /api/orders/create/` — оформить заказ
- `GET /api/orders/<id>/` — детали заказа
- `PATCH /api/orders/<id>/status/` — изменить статус администратору
- `POST /api/partner/update/` — импорт прайса поставщика
- `POST /api/partner/state/` — включить/выключить приём заказов
- `GET /api/partner/orders/` — просмотр заказов поставщика

## Импорт

По умолчанию используется файл `data/shop1.yaml`:

```bash
python manage.py import_products
```

Также можно передать путь к своему YAML или URL:

```bash
python manage.py import_products data/shop1.yaml
```

## Docker

Для продвинутой части:

```bash
docker compose up --build
```

В Docker Celery работает через Redis.

## Проверка

```bash
python manage.py check
python manage.py test
```

Тесты находятся в `tests/`.
