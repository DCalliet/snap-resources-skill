from mycroft import MycroftSkill, intent_file_handler
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.audio import wait_while_speaking
from mycroft.skills.context import *


class SnapResourceSkill(MycroftSkill):
    '''
        This skill has a dialogue for determining snap eligibility.
    '''
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('snap.eligibility.intent')
    def handle_resources_snap(self, message):
        self.speak_dialog('snap.eligibility')
        wait_while_speaking()
        eligibility_info = self.ask_yesno('snap.more.info')
        wait_while_speaking()
        if eligibility_info == "yes":
            self.citizen = self.ask_yesno('citizen')
            wait_while_speaking()
            if not self.citizen:
                self.five_years = self.ask_yesno('five.years')
                wait_while_speaking()

            if self.citizen or self.five_years:
                self.employment = self.ask_yesno('employment')
                wait_while_speaking()
                if self.employment:
                    self.income = self.ask_yesno('income')
                    wait_while_speaking()

                    if self.income:
                        self.speak_dialog('generic.yes')
                    else:
                        self.speak_dialog('generic.no')
        else:
            self.speak_dialog('here.to.assist')
            wait_while_speaking()

def create_skill():
    return SnapResourceSkill()
