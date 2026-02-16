import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from app.database import Base, SessionLocal, engine
from app.models import (
    Building,
    Business,
    Organization,
    OrganizationBusiness,
    Phone,
)

print(f"БД будет создана по пути: {Path('database.db').absolute()}")
print(f"Текущая директория: {Path.cwd()}")


def seed_database():
    db = SessionLocal()
    try:
        # Проверяем, пустая ли БД
        if db.query(Building).count() > 0:
            print("БД уже содержит данные — пропускаем наполнение.")
            return

        # Здания
        buildings_data = [
            {
                "address": "ул. Ленина, 1, офис 3",
                "latitude": 55.7558,
                "longitude": 37.6176,
            },
            {
                "address": "пр. Мира, 15, БЦ 'Мир'",
                "latitude": 55.7601,
                "longitude": 37.6325,
            },
            {
                "address": "ул. Тверская, 7, офис 12",
                "latitude": 55.7652,
                "longitude": 37.6034,
            },
            {
                "address": "ул. Новый Арбат, 24",
                "latitude": 55.7528,
                "longitude": 37.5973,
            },
            {
                "address": "ул. Мясницкая, 30/1/2",
                "latitude": 55.7625,
                "longitude": 37.6398,
            },
            {
                "address": "пр. Вернадского, 78",
                "latitude": 55.6602,
                "longitude": 37.4805,
            },
            {
                "address": "ул. Профсоюзная, 61",
                "latitude": 55.6421,
                "longitude": 37.5325,
            },
            {
                "address": "Ленинградский пр-т, 80",
                "latitude": 55.8021,
                "longitude": 37.5132,
            },
            {
                "address": "ул. 1905 года, 7",
                "latitude": 55.7658,
                "longitude": 37.5612,
            },
            {
                "address": "Бережковская наб., 20",
                "latitude": 55.7321,
                "longitude": 37.5543,
            },
        ]

        buildings = []
        for b_data in buildings_data:
            building = Building(**b_data)
            db.add(building)
            buildings.append(building)
        db.flush()  # чтобы получить id

        # Виды деятельности
        # Уровень 1
        food = Business(name="Еда")
        cars = Business(name="Автомобили")
        it = Business(name="IT и технологии")
        health = Business(name="Медицина и здоровье")
        education = Business(name="Образование")

        db.add_all([food, cars, it, health, education])
        db.flush()

        # Уровень 2
        meat = Business(name="Мясная продукция", parent_id=food.id)
        dairy = Business(name="Молочная продукция", parent_id=food.id)
        bakery = Business(name="Хлебобулочные изделия", parent_id=food.id)

        trucks = Business(name="Грузовые автомобили", parent_id=cars.id)
        passenger = Business(name="Легковые автомобили", parent_id=cars.id)
        auto_parts = Business(name="Автозапчасти", parent_id=cars.id)

        software = Business(name="Разработка ПО", parent_id=it.id)
        hardware = Business(name="Компьютерная техника", parent_id=it.id)

        clinics = Business(name="Клиники", parent_id=health.id)
        pharmacy = Business(name="Аптеки", parent_id=health.id)

        schools = Business(name="Школы", parent_id=education.id)
        universities = Business(name="ВУЗы", parent_id=education.id)

        db.add_all(
            [
                meat,
                dairy,
                bakery,
                trucks,
                passenger,
                auto_parts,
                software,
                hardware,
                clinics,
                pharmacy,
                schools,
                universities,
            ]
        )
        db.flush()

        # Уровень 3
        diagnostic = Business(name="Диагностика автомобилей", parent_id=auto_parts.id)
        tires = Business(name="Шины и диски", parent_id=auto_parts.id)

        web = Business(name="Веб-разработка", parent_id=software.id)
        mobile = Business(name="Мобильные приложения", parent_id=software.id)

        dentistry = Business(name="Стоматология", parent_id=clinics.id)

        db.add_all([diagnostic, tires, web, mobile, dentistry])
        db.flush()

        # Организации
        organizations_data = [
            (
                "ООО 'Рога и Копыта'",
                0,
                [meat, dairy],
                ["+7 (495) 123-45-67", "+7 (495) 765-43-21"],
            ),
            (
                "Мясной Дом 'Богатырь'",
                1,
                [meat],
                ["+7 (495) 234-56-78", "8-800-555-35-35"],
            ),
            ("Молоко-Завод №1", 2, [dairy], ["+7 (495) 345-67-89"]),
            (
                "Пекарня 'Хлебосол'",
                3,
                [bakery],
                ["+7 (495) 456-78-90", "+7 (916) 123-45-67"],
            ),
            (
                "Автосалон 'Премиум'",
                4,
                [passenger],
                ["+7 (495) 567-89-01", "+7 (925) 555-66-77"],
            ),
            ("Грузовик-Центр", 5, [trucks], ["+7 (495) 678-90-12"]),
            (
                "Запчасти-24",
                6,
                [auto_parts, diagnostic],
                ["+7 (495) 789-01-23", "8-800-222-33-44"],
            ),
            ("Шинный центр", 7, [tires], ["+7 (495) 890-12-34"]),
            (
                "IT-Групп 'Софт'",
                8,
                [software, web],
                ["+7 (495) 901-23-45", "+7 (903) 111-22-33"],
            ),
            ("Мобильные Решения", 9, [mobile], ["+7 (495) 012-34-56"]),
            (
                "Компьютерный Мир",
                0,
                [hardware],
                ["+7 (495) 123-45-67", "+7 (495) 234-56-78"],
            ),
            (
                "Клиника 'Здоровье'",
                1,
                [clinics, dentistry],
                ["+7 (495) 345-67-89", "8-800-777-88-99"],
            ),
            ("Аптека 'Фарма'", 2, [pharmacy], ["+7 (495) 456-78-90"]),
            ("Школа №42", 3, [schools], ["+7 (495) 567-89-01"]),
            (
                "МГУ имени Ломоносова",
                4,
                [universities],
                ["+7 (495) 678-90-12", "+7 (495) 789-01-23"],
            ),
            ("Стоматология 'Дент'", 5, [dentistry], ["+7 (495) 890-12-34"]),
            ("Ресторан 'Еда'", 6, [food], ["+7 (495) 901-23-45"]),
            ("Пивоварня 'Жигули'", 7, [food], ["+7 (495) 012-34-56"]),
            ("Автосервис 'Профи'", 8, [diagnostic, tires], ["+7 (495) 123-45-67"]),
            (
                "IT-Академия",
                9,
                [education, software],
                ["+7 (495) 234-56-78", "+7 (915) 333-44-55"],
            ),
        ]

        organizations = []
        for name, building_idx, businesses_list, phones_list in organizations_data:
            org = Organization(name=name, building_id=buildings[building_idx].id)
            db.add(org)
            organizations.append(org)
        db.flush()

        # Телефоны
        for i, (_, _, _, phones_list) in enumerate(organizations_data):
            for phone_number in phones_list:
                phone = Phone(number=phone_number, organization_id=organizations[i].id)
                db.add(phone)

        # Связи организаций с бизнесами
        for i, (_, _, businesses_list, _) in enumerate(organizations_data):
            for business in businesses_list:
                org_business = OrganizationBusiness(
                    organization_id=organizations[i].id, business_id=business.id
                )
                db.add(org_business)

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Ошибка при наполнении БД: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_database()
