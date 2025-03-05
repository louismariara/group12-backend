from extensions import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Association table for many-to-many relationship between Student and Course
student_course = db.Table('student_course',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.LargeBinary, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_instructor = db.Column(db.Boolean, default=False)
    is_student = db.Column(db.Boolean, default=False)

    def validate_roles(self):
        if self.id == 1:
            if not self.is_admin or self.is_instructor or self.is_student:
                raise ValueError("User with id=1 must be admin only.")
        else:
            if self.is_admin:
                raise ValueError("Only user with id=1 can be an admin.")
        if self.is_instructor and self.is_student:
            raise ValueError("A user cannot be both an instructor and a student.")

class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    is_student = db.Column(db.Boolean, default=True)
    courses = db.relationship('Course', secondary=student_course, backref=db.backref('students', lazy='dynamic'))

class Instructor(db.Model):
    __tablename__ = "instructor"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    is_instructor = db.Column(db.Boolean, default=True)
    # Removed course_id and course relationship

class Course(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey("instructor.id"), nullable=True)
    image = db.Column(db.String(255), nullable=True)  # Store image path or URL
    modules = db.Column(db.JSON, nullable=True)  # Store modules as JSON (e.g., list of dictionaries)
    instructor = db.relationship(
        "Instructor", backref=db.backref("courses", lazy="dynamic"), foreign_keys=[instructor_id]
    )
class Grade(db.Model):
    __tablename__ = "grade"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    comments = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', backref=db.backref('grades', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('grades', lazy='dynamic'))