from flask_marshmallow import Marshmallow
from models import Student, Course, Instructor, Grade, User
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

ma = Marshmallow()

class StudentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        include_relationships = True
        load_instance = True

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = False
        load_instance = True
        exclude = ["password"]

class CourseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Course
        include_fk = True
        include_relationships = True  # Enable relationships for students
        load_instance = True
        # Remove created_at from exclude to include it

    image = auto_field("image", allow_none=True)
    modules = auto_field("modules", allow_none=True)
    name = auto_field(required=True)
    duration = auto_field(required=True)
    created_at = auto_field(allow_none=True)  # Explicitly include
    students = ma.Nested(UserSchema, many=True, only=("id",))  # Serialize student IDs

class InstructorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Instructor
        include_fk = True
        load_instance = True

class GradeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Grade
        include_relationships = True
        load_instance = True

    grade = auto_field(type_=str, required=True)
    student_id = auto_field(required=True)
    course_id = auto_field(required=True)
    comments = auto_field(allow_none=True)