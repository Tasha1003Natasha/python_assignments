from sqlalchemy import select, func
from db_config import DBSession
from models import Group, Student, Teacher, Subject, Grade


def select_1():
    with DBSession() as session:
        result = (
            session.query(
                Student.fullname,
                func.round(func.avg(Grade.grade), 2).label("avg_grade"),
            )
            .join(Grade)
            .group_by(Student.id)
            .order_by(func.avg(Grade.grade).desc())
            .limit(5)
            .all()
        )

        return result


def select_2(subject_id=1):
    with DBSession() as session:
        result = (
            session.query(
                Student.fullname,
                Subject.name,
                func.round(
                    func.avg(Grade.grade), 2
                ).label("avg_grade"),
            )
            .join(Grade, Grade.student_id == Student.id)
            .join(Subject, Grade.subject_id == Subject.id)
            .filter(Subject.id == subject_id)
            .group_by(
                Student.id,
                Student.fullname,
                Subject.id,
                Subject.name,
            )
            .order_by(
                func.avg(Grade.grade).desc()
            )
            .first()
        )

        return result


def select_3(subject_id=1):
    with DBSession() as session:
        result = (
            session.query(
                Group.name,
                Subject.name,
                func.round(
                    func.avg(Grade.grade), 2
                ).label("avg_grade"),
            )
            .join(Student, Student.group_id == Group.id)
            .join(Grade, Grade.student_id == Student.id)
            .join(Subject, Subject.id == Grade.subject_id)
            .filter(Subject.id == subject_id)
            .group_by(
                Group.id,
                Subject.name,
                Subject.id,
            )
            .order_by(
                func.avg(Grade.grade).desc()
            )
            .all()
        )

        return result


def select_4():
    with DBSession() as session:
        result = (
            session.query(
                func.round(
                    func.avg(Grade.grade), 2
                ).label("avg_grade"),
            )
            .scalar()
        )

        return result


def select_5(teacher_id=1):
    with DBSession() as session:
        result = (
            session.query(
                Teacher.fullname,
                Subject.name,
            )
            .join(Subject, Subject.teacher_id == Teacher.id)
            .filter(Teacher.id == teacher_id)
            .all()
        )

        return result


def select_6(group_id=1):
    with DBSession() as session:
        result = (
            session.query(
                Student.fullname,
            )
            .join(Group, Group.id == Student.group_id)
            .filter(Group.id == group_id)
            .all()
        )

        return result


def select_7(group_id=1, subject_id=1):
    with DBSession() as session:
        result = (
            session.query(
                Student.fullname,
                Subject.name,
                Grade.grade
            )
            .join(Group, Group.id == Student.group_id)
            .join(Grade, Grade.student_id == Student.id)
            .join(Subject, Subject.id == Grade.subject_id)
            .filter(Group.id == group_id, Subject.id == subject_id)
            .all()

        )

        return result


def select_8(teacher_id=1):
    with DBSession() as session:
        result = (
            session.query(
                Teacher.fullname,
                func.round(
                    func.avg(Grade.grade), 2
                ).label("avg_grade"),
            )
            .join(Subject, Subject.id == Grade.subject_id)
            .join(Teacher, Teacher.id == Subject.teacher_id)
            .filter(Teacher.id == teacher_id)
            .group_by(
                Teacher.fullname,
            )
            .order_by(
                func.avg(Grade.grade).desc()
            )
            .all()
        )

        return result


def select_9(student_id=1):
    with DBSession() as session:
        result = (
            session.query(
                Student.fullname,
                Subject.name,

            )
            .join(Grade, Grade.student_id == Student.id)
            .join(Subject,  Subject.id == Grade.subject_id)
            .filter(Student.id == student_id)
            .distinct()
            .all()
        )
        return result


def select_10(teacher_id=1, student_id=1):
    with DBSession() as session:
        result = (
            session.query(
                Student.fullname,
                Subject.name,
                Teacher.fullname
            )
            .join(Grade, Grade.student_id == Student.id)
            .join(Subject,  Subject.id == Grade.subject_id)
            .join(Teacher,  Teacher.id == Subject.teacher_id)
            .filter(Student.id == student_id, Teacher.id == teacher_id)
            .distinct()
            .all()
        )
        return result


def select_11(teacher_id=1, student_id=1):
    with DBSession() as session:
        result = (
            session.query(
                Student.fullname,
                Teacher.fullname,
                func.round(
                    func.avg(Grade.grade), 2
                ).label("avg_grade"),
            )
            .join(Grade, Grade.student_id == Student.id)
            .join(Subject,  Subject.id == Grade.subject_id)
            .join(Teacher,  Teacher.id == Subject.teacher_id)
            .filter(Student.id == student_id, Teacher.id == teacher_id)
            .group_by(
                Student.fullname,
                Teacher.fullname,
            )
            .order_by(
                func.avg(Grade.grade).desc()
            )
            .first()
        )
        return result


def select_12(group_id=1, subject_id=1):
    with DBSession() as session:

        last_grade_date = (
            select(
                func.max(Grade.date_of)
            )
            .join(Student, Student.id == Grade.student_id)
            .filter(
                Student.group_id == group_id,
                Grade.subject_id == subject_id,
            )
            .scalar_subquery()
        )

        result = (
            session.query(
                Student.fullname,
                Group.name,
                Subject.name,
                Grade.grade,
                Grade.date_of
            )
            .join(Group, Group.id == Student.group_id)
            .join(Grade, Grade.student_id == Student.id)
            .join(Subject,  Subject.id == Grade.subject_id)
            .filter(Group.id == group_id, Subject.id == subject_id, Grade.date_of == last_grade_date)
            .all()
        )
        return result


if __name__ == "__main__":
    result = select_1()
