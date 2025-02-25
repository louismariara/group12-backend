from flask_marshmallow import Marshmallow
from models import Student, Course, Instructor, Grade 

ma = Marshmallow() 

class StudentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        include_relationships = True
        load_instance = True

class CourseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Course
        include_fk = True
        load_instance = True

class InstructorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Instructor
        include_fk = True
        load_instance = True

class GradeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Grade
        include_relationships = True
        load_instance = True