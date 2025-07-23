from enum import Enum
from bs4 import BeautifulSoup
import json
try:
   from person import GSPerson
   from person import GSRole
except ModuleNotFoundError:
   from .person import GSPerson
   from .person import GSRole
try:
   from assignment import GSAssignment
except ModuleNotFoundError:
   from .assignment import GSAssignment

AID_GLOBAL = "6405282"

class LoadedCapabilities(Enum):
    ASSIGNMENTS = 0
    ROSTER = 1

class GSCourse():

    def __init__(self, cid, session):
        '''Create a course object that has lazy eval'd assignments'''
        self.cid = cid
        self.session = session
        self.assignments = {}
        self.state = set() # Set of already loaded entitites (TODO what is the pythonic way to do this?)

    # ~~~~~~~~~~~~~~~~~~~~~~HOUSEKEEPING~~~~~~~~~~~~~~~~~~~~~~~~~

    def _lazy_load_assignments(self):
        '''
        Load the assignment dictionary from assignments. This is done lazily to avoid slowdown caused by getting
        all the assignments for all classes. Also makes us less vulnerable to blocking.
        '''
        assignment_resp = self.session.get('https://www.gradescope.com/courses/'+self.cid+'/assignments')
        parsed_assignment_resp = BeautifulSoup(assignment_resp.text, 'html.parser')
        
        div = parsed_assignment_resp.select_one('div[data-react-class="AssignmentsTable"]')
        data = json.loads(div['data-react-props'])
        rows = data['table_data']  # list of dicts
        assignment_table = []
        for row in rows:
            if row['type'] == 'assignment':
                aid = row['id'].split('_', 1)[1]
                name = row['title']
                assignment_table.append((aid,name))
        
        for aid, name in assignment_table:
            if (aid != AID_GLOBAL):
                continue
            print("Loading AID: " + aid)
            self.assignments[aid] = GSAssignment(name, aid, self)
        self.state.add(LoadedCapabilities.ASSIGNMENTS)
        pass
        
    def _check_capabilities(self, needed):
        '''
        checks if we have the needed data loaded and gets them lazily.
        '''
        missing = needed - self.state
        if LoadedCapabilities.ASSIGNMENTS in missing:
            self._lazy_load_assignments()
        if LoadedCapabilities.ROSTER in missing:
            self._lazy_load_roster()

    def delete(self):
        course_edit_resp = self.session.get('https://www.gradescope.com/courses/'+self.cid+'/edit')
        parsed_course_edit_resp = BeautifulSoup(course_edit_resp.text, 'html.parser')

        authenticity_token = parsed_course_edit_resp.find('meta', attrs = {'name': 'csrf-token'} ).get('content')

        print(authenticity_token)

        delete_params = {
            "_method": "delete",
            "authenticity_token": authenticity_token
        }
        print(delete_params)

        delete_resp = self.session.post('https://www.gradescope.com/courses/'+self.cid,
                                        data = delete_params,
                                        headers={
                                            'referer': 'https://www.gradescope.com/courses/'+self.cid+'/edit',
                                            'origin': 'https://www.gradescope.com'
                                        })
        
        # TODO make this less brittle 
