from flask_marshmallow import Marshmallow
<<<<<<< HEAD
from models import Student, Course, Instructor, Grade
=======
from models import Student, Course, Instructor, Grade, User 
>>>>>>> c5c057fbb3c9c7ecd00378e3b84402c5893f565d

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
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = False
        load_instance = True
        exclude = ['password']