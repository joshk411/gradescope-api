import requests
from bs4 import BeautifulSoup
try:
   from question import GSQuestion
except ModuleNotFoundError:
   from .question import GSQuestion
import json

class GSAssignment():

    def __init__(self, name, aid, course):
        '''Create a assignment object'''
        self.name = name
        self.aid = aid
        self.course = course
        self.questions = []

    def view_prev_submissions(self, sid):
        prev_sub_resp = self.course.session.get('https://www.gradescope.com/courses/' + self.course.cid +
                                               '/assignments/' + self.aid + '/submissions/' + sid + '.json?content=react&only_keys[]=past_submissions')
        prev_sub_resp.raise_for_status()
        data = prev_sub_resp.json()
        flag = False
        current_explosion = 0.0
        prev_explosion = 0.0
        for submission in data['past_submissions']:
            sub_path = submission['show_path']
            resp = self.course.session.get('https://www.gradescope.com' + sub_path + '.json')
            resp_data = resp.json()
            for test in resp_data['results']['tests']:
                if (test['name'] == 'explosion'):       # Initial testing with SFS fields
                    current_explosion = test['score']

            # The current explosion score (negative) should always be more negative or equal
            if (prev_explosion < current_explosion):
                flag = True
            # Update previous count
            prev_explosion = current_explosion
        
        return flag
            