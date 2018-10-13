from mycroft import MycroftSkill, intent_file_handler
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.audio import wait_while_speaking
from mycroft.skills.context import *

import time

class SnapResourceSkill(MycroftSkill):
    '''
        This skill has a dialogue for determining snap eligibility.

        Where can I go for more snap info?

        Am I eligible for food stamps?
    '''


    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('snap.eligibility.intent')
    def handle_resources_snap(self, message):
        is_yes = lambda x: (x == "yes")
        is_no = lambda x: (x == "no")
        self.speak_dialog('snap.eligibility')
        wait_while_speaking()

        time.sleep(5)
        eligibility_info = self.ask_yesno('snap.more.info')
        wait_while_speaking()

        if is_yes(eligibility_info):
            self.record_info = self.ask_yesno('collect.more.info')

            if is_yes(self.record_info):
                self.phone_number = self.get_response('ask.phone.number')

            self.citizen = self.ask_yesno('citizen')
            wait_while_speaking()
            if is_no(self.citizen):
                self.five_years = self.ask_yesno('five.years')
                wait_while_speaking()

            if is_yes(self.citizen) or is_yes(self.five_years):
                self.employment = self.ask_yesno('employment')
                wait_while_speaking()
                if is_yes(self.employment):
                    self.income = self.ask_yesno('income')
                    wait_while_speaking()

                    if is_yes(self.income):
                        self.speak_dialog('generic.yes')
                    else:
                        self.speak_dialog('generic.no')
        else:
            self.speak_dialog('here.to.assist')
            wait_while_speaking()

def create_skill():
    return SnapResourceSkill()
