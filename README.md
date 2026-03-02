# Organization Catalog API

FastAPI-сервис для управления каталогом организаций с поддержкой геопоиска, древовидной классификации видов деятельности и полнотекстового поиска.

## Функционал
- Получение списка всех организаций, находящихся в конкретном здании
- Получение списка всех организаций, относящихся к указанному виду деятельности
- Поиск организаций и зданий в заданной области: круг (по радиусу) или прямоугольник (bounding box)
- Получение полной информации об организации по её идентификатору
- Рекурсивный поиск организаций по виду деятельности с учётом вложенности (до 3 уровней): при запросе «Еда» находятся также «Мясная продукция», «Молочная продукция» и другие подкатегории
- Поиск организаций по названию (регистронезависимый, частичное совпадение)
- Ограничение глубины дерева видов деятельности тремя уровнями
- Защита API статическим ключом

## Структура проекта

```text
organization-catalog-api/
├──📁app/
│   ├── __init__.py
│   ├── database.py                       # Подключение к БД
│   ├── models.py                         # SQLAlchemy модели
│   ├── schemas.py                        # Pydantic схемы
│   ├── utils.py                          # Вспомогательные функции (гео, дерево)
│   ├── dependencies.py                   # Проверка API-ключа
│   │
│   └──📁routers/
│       ├── __init__.py
│       ├── buildings.py                  # Эндпоинты по зданиям
│       ├── businesses.py                 # Эндпоинты по типам деятельности
│       └── organizations.py              # Эндпоинты по организациям
│
├──📁sql/
│   ├── dataschema.sql                    # Схема БД в SQL
│   ├── db_schema.png                     # Скриншот схемы БД
│   └── seed_data.py                      # Наполнение тестовыми данными
│
├──📁migrations/                         # Миграции
│
├── .env.example                          # Пример для переменных окружения
├── alembic.ini                           # Конфигурация Alembic
├── Dockerfile                            # Конфигурация Docker
├── main.py                               # Точка входа
├── requirements.txt                      # Зависимости
├── README.md                             # Документация
└── database.db                           # SQLite БД
```

## Установка и запуск

### 1. Локальный запуск (без Docker)

```bash
# Установка зависимостей
pip install -r requirements.txt
```
```bash
# Применение миграций
alembic upgrade head
```

```bash
# Наполнение данными
python sql/seed_data.py
```

```bash
# Запуск приложения
uvicorn main:app --reload
```

Приложение доступно по адресу: http://localhost:8000

### 2. Запуск через Docker

> 💡 Создайте .env и добавьте ключ!

```bash
# Сборка образа
docker build -t org-catalog-api .
```

```bash
# Запуск контейнера
docker run -p 8000:8000 org-catalog-api
```

Приложение развёрнуто и доступно по адресу: http://149.154.70.253:8000
> 💡 А ключ к нему сами знаете где 😈

## API Endpoints

Все запросы должны содержать заголовок:
X-API-Key: secret


### Health Check
**GET /**   

**Заголовки:**
X-API-Key: secret

**Ответ (200 OK):**
```json
{
  "service": "Organization Catalog Api",
  "health": "OK",
  "author": "Sergey Naryshkin",
  "description": "Тестовое задание на должность разработчика"
}
```

### Организации в здании
**GET organizations/building/1**

Запрос
```bash
curl -H "X-API-Key: secret" http://localhost:8000/organizations/building/1
```

Ответ (200 OK)
```json
[
  {
    "id": 1,
    "name": "Кофейня 'Аромат'",
    "phones": ["+74951234567", "+74957654321"],
    "businesses": [
      {"id": 1, "name": "Еда", "parent_id": null},
      {"id": 4, "name": "Кофейни", "parent_id": 1}
    ],
    "building": {
      "id": 1,
      "address": "ул. Ленина, 1",
      "latitude": 55.7558,
      "longitude": 37.6176
    }
  },
  {
    "id": 2,
    "name": "Аптека 'Здоровье'",
    "phones": ["+74959876543"],
    "businesses": [
      {"id": 2, "name": "Здравоохранение", "parent_id": null},
      {"id": 5, "name": "Аптеки", "parent_id": 2}
    ],
    "building": {
      "id": 1,
      "address": "ул. Ленина, 1",
      "latitude": 55.7558,
      "longitude": 37.6176
    }
  }
]
```

Ошибки:
- 404 Not Found: {"detail": "Здание с ID 999 не найдено"}

### Организации по виду деятельности
**GET /organizations/business/1**

Запрос
```bash
curl -H "X-API-Key: secret" http://localhost:8000/organizations/business/1
```

Ответ (200 OK)
```json
[
  {
    "id": 1,
    "name": "Кофейня 'Аромат'",
    "phones": ["+74951234567", "+74957654321"],
    "businesses": [
      {"id": 1, "name": "Еда", "parent_id": null},
      {"id": 4, "name": "Кофейни", "parent_id": 1}
    ],
    "building": {
      "id": 1,
      "address": "ул. Ленина, 1",
      "latitude": 55.7558,
      "longitude": 37.6176
    }
  },
  {
    "id": 3,
    "name": "Кофейня 'Латте'",
    "phones": ["+73474445566"],
    "businesses": [
      {"id": 1, "name": "Еда", "parent_id": null},
      {"id": 4, "name": "Кофейни", "parent_id": 1}
    ],
    "building": {
      "id": 3,
      "address": "ул. Карла Маркса, 10",
      "latitude": 56.8389,
      "longitude": 60.6057
    }
  }
]
```

Ошибки:
- 404 Not Found: {"detail": "Вид деятельности с ID 999 не найден"}

### Рекурсивный поиск по бизнесу
**GET businesses/1/organizations**
 
Запрос
```bash
curl -H "X-API-Key: secret" http://localhost:8000/organizations/business/1
```

Ответ (200 OK)
```json
[
  {
    "id": 1,
    "name": "Кофейня 'Аромат'",
    "phones": ["+74951234567", "+74957654321"],
    "businesses": [
      {"id": 1, "name": "Еда", "parent_id": null},
      {"id": 4, "name": "Кофейни", "parent_id": 1},
      {"id": 7, "name": "Кофейни премиум-класса", "parent_id": 4}
    ],
    "building": {
      "id": 1,
      "address": "ул. Ленина, 1",
      "latitude": 55.7558,
      "longitude": 37.6176
    }
  },
  {
    "id": 4,
    "name": "Молочный магазин 'Ферма'",
    "phones": ["+73474445566"],
    "businesses": [
      {"id": 1, "name": "Еда", "parent_id": null},
      {"id": 3, "name": "Молочная продукция", "parent_id": 1},
      {"id": 8, "name": "Сыры", "parent_id": 3}
    ],
    "building": {
      "id": 4,
      "address": "ул. Пушкина, 15",
      "latitude": 54.7348,
      "longitude": 55.9678
    }
  }
]
```

Ошибки:
- 404 Not Found: {"detail": "Вид деятельности с ID 999 не найден"}

### Информация об организации
**GET organizations/1**

Запрос
```bash
curl -H "X-API-Key: secret" http://localhost:8000/organizations/1
```

Ответ (200 OK)
```json
{
  "id": 1,
  "name": "Кофейня 'Аромат'",
  "phones": ["+74951234567", "+74957654321"],
  "businesses": [
    {"id": 1, "name": "Еда", "parent_id": null},
    {"id": 4, "name": "Кофейни", "parent_id": 1},
    {"id": 7, "name": "Кофейни премиум-класса", "parent_id": 4}
  ],
  "building": {
    "id": 1,
    "address": "ул. Ленина, 1",
    "latitude": 55.7558,
    "longitude": 37.6176
  }
}
```

Ошибки
- 404 Not Found: {"detail": "Организация с ID 999 не найдена"}

### Поиск по названию
**GET organizations/search**

Запрос
```bash
curl -H "X-API-Key: secret" "http://localhost:8000/organizations/search?name=рога"
```

Ответ (200 OK)
```json
[
  {
    "id": 1,
    "name": "Кофейня 'Аромат'",
    "phones": ["+74951234567", "+74957654321"],
    "businesses": [
      {"id": 1, "name": "Еда", "parent_id": null},
      {"id": 4, "name": "Кофейни", "parent_id": 1}
    ],
    "building": {
      "id": 1,
      "address": "ул. Ленина, 1",
      "latitude": 55.7558,
      "longitude": 37.6176
    }
  },
  {
    "id": 3,
    "name": "Кофейня 'Латте'",
    "phones": ["+73474445566"],
    "businesses": [
      {"id": 1, "name": "Еда", "parent_id": null},
      {"id": 4, "name": "Кофейни", "parent_id": 1}
    ],
    "building": {
      "id": 3,
      "address": "ул. Карла Маркса, 10",
      "latitude": 56.8389,
      "longitude": 60.6057
    }
  }
]
```

### Геопоиск организаций
**GET organizations/nearby**

Запрос
```bash
curl -H "X-API-Key: secret" "http://localhost:8000/organizations/nearby?lat=55.7558&lon=37.6176&radius=1000&shape=circle"
```

Ответ (200 OK)
```json
[
  {
    "id": 1,
    "name": "Кофейня 'Аромат'",
    "phones": ["+74951234567", "+74957654321"],
    "businesses": [
      {"id": 1, "name": "Еда", "parent_id": null},
      {"id": 4, "name": "Кофейни", "parent_id": 1}
    ],
    "building": {
      "id": 1,
      "address": "ул. Ленина, 1",
      "latitude": 55.7558,
      "longitude": 37.6176
    }
  },
  {
    "id": 2,
    "name": "Аптека 'Здоровье'",
    "phones": ["+74959876543"],
    "businesses": [
      {"id": 2, "name": "Здравоохранение", "parent_id": null},
      {"id": 5, "name": "Аптеки", "parent_id": 2}
    ],
    "building": {
      "id": 1,
      "address": "ул. Ленина, 1",
      "latitude": 55.7558,
      "longitude": 37.6176
    }
  }
]
```

### Геопоиск зданий
**GET buildings/nearby**
 
Запрос
```bash
curl -H "X-API-Key: secret" "http://localhost:8000/buildings/nearby?lat=55.7558&lon=37.6176&radius=1000&shape=square"
```

Ответ (200 OK)
```json
[
  {
    "id": 1,
    "address": "ул. Ленина, 1",
    "latitude": 55.7558,
    "longitude": 37.6176
  },
  {
    "id": 2,
    "address": "Невский проспект, 28",
    "latitude": 59.9343,
    "longitude": 30.3351
  }
]
```

## Документация API
> 💡 Не забудьте добавить ключ!

Swagger UI: http://149.154.70.253:8000/docs  
ReDoc: http://149.154.70.253:8000/redoc

## Модель данных
База данных включает 5 таблиц:
- `building` - здания с координатами
- `organization` - организации (связь с зданием)
- `phone` - телефоны организаций
- `business` - виды деятельности (дерево до 3 уровней)
- `organization_business` - связь многие-ко-многим
<br></br>

<div align="center">

![Схема БД](/sql/db_schema.png)  
*Схема базы данных*

</div>
