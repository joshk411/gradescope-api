from bs4 import BeautifulSoup
try:
   from course import GSCourse
except ModuleNotFoundError:
   from .course import GSCourse

class GSAccount():
    '''A class designed to track the account details (instructor and student courses'''

    def __init__(self, email, session):
        self.email = email
        self.session = session
        self.instructor_courses = {}
        self.student_courses = {}

    def add_class(self, cid, instructor = False):
        if instructor:
            self.instructor_courses[cid] = GSCourse(cid, self.session)
        else:
            self.student_courses[cid] = GSCourse(cid, self.session)
        
