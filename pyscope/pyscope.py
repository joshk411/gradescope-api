import requests
from bs4 import BeautifulSoup
from enum import Enum
try:
   from account import GSAccount
except ModuleNotFoundError:
   from .account import GSAccount

try:
   from course import GSCourse
except ModuleNotFoundError:
   from .course import GSCourse

CID_GLOBAL = "1040746"  # Course ID

class ConnState(Enum):
    INIT = 0
    LOGGED_IN = 1

class GSConnection():
    '''The main connection class that keeps state about the current connection.'''
        
    def __init__(self):
        '''Initialize the session for the connection.'''
        self.session = requests.Session()
        self.state = ConnState.INIT
        self.account = None

    def login(self, email, pswd):
        '''
        Login to gradescope using email and password.
        Note that the future commands depend on account privilages.
        '''
        init_resp = self.session.get("https://www.gradescope.com/")
        parsed_init_resp = BeautifulSoup(init_resp.text, 'html.parser')
        for form in parsed_init_resp.find_all('form'):
            if form.get("action") == "/login":
                for inp in form.find_all('input'):
                    if inp.get('name') == "authenticity_token":
                        auth_token = inp.get('value')

        login_data = {
            "utf8": "✓",
            "session[email]": email,
            "session[password]": pswd,
            "session[remember_me]": 0,
            "commit": "Log In",
            "session[remember_me_sso]": 0,
            "authenticity_token": auth_token,
        }
        login_resp = self.session.post("https://www.gradescope.com/login", params=login_data)
        if len(login_resp.history) != 0:
            if login_resp.history[0].status_code == requests.codes.found:
                self.state = ConnState.LOGGED_IN
                self.account = GSAccount(email, self.session)
                print("Succesfully logged in")
                return True
        else:
            return False

    def get_account(self):
        '''
        Gets and parses account data after login. Note will return false if we are not in a logged in state, but 
        this is subject to change.
        '''
        if self.state != ConnState.LOGGED_IN:
            return False
        # Get account page and parse it using bs4
        account_resp = self.session.get("https://www.gradescope.com/account")
        parsed_account_resp = BeautifulSoup(account_resp.text, 'html.parser')

        # Get instructor course data
        instructor_courses = parsed_account_resp.find('h1', class_ ='pageHeading').next_sibling
        
        for course in instructor_courses.find_all('a', class_ = 'courseBox'):
            cid = course.get("href").split("/")[-1]
            if (cid != CID_GLOBAL):
                continue
            print("CID = " + cid)
            self.account.add_class(cid, instructor = True)
        return True

