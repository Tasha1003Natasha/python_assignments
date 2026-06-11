from datetime import datetime, timedelta
import faker
from random import choice, randint
import random
from sqlalchemy.exc import SQLAlchemyError


from db_config import DBSession
from models import Group, Student, Teacher, Subject, Grade


NUMBER_GROUPS = 3
NUMBER_STUDENTS = random.randint(30, 50)
NUMBER_TEACHERS = random.randint(3, 5)
NUMBER_SUBJECTS = random.randint(5, 8)
NUMBER_GREADES = random.randint(10, 20)


fake = faker.Faker("uk_UA")


def seed_data():
    with DBSession() as session:

        groups = [
            Group(name=f"Group-{i}")
            for i in range(1, NUMBER_GROUPS + 1)
        ]
        session.add_all(groups)
        session.commit()

        teachers = [
            Teacher(fullname=fake.name())
            for _ in range(NUMBER_TEACHERS)
        ]
        session.add_all(teachers)
        session.commit()

        subjects = [
            Subject(
                name=fake.word().capitalize(),
                teacher_id=choice(teachers).id,
            )
            for _ in range(NUMBER_SUBJECTS)
        ]
        session.add_all(subjects)
        session.commit()

        students = [
            Student(
                fullname=fake.name(),
                group_id=choice(groups).id,
            )
            for _ in range(NUMBER_STUDENTS)
        ]
        session.add_all(students)
        session.commit()

        grades = []

        for student in students:

            for _ in range(NUMBER_GREADES):

                random_days = randint(1, 365)
                grade_date_of = (
                    datetime.now() - timedelta(days=random_days)
                ).date()

                grades.append(
                    Grade(
                        grade=randint(1, 12),
                        date_of=grade_date_of,
                        student_id=student.id,
                        subject_id=choice(subjects).id,
                    )
                )

        session.add_all(grades)
        session.commit()


if __name__ == "__main__":
    try:
        seed_data()
        print("Database seeded successfully")
    except SQLAlchemyError as error:
        print(error)
