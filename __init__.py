from mycroft import MycroftSkill, intent_file_handler
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.audio import wait_while_speaking
from mycroft.skills.context import *


class SnapResources(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('green.card.intent')
    def handle_resources_citizenship(self, message):
        self.speak_dialog('green.card.eligibility')
        eligibility_info = self.ask_yesno('eligibility.more.info')
        if eligibility_info == 'yes':
            self.speak_dialog('list.eligibility')
        else:
            self.speak_dialog('here.to.assist')


def create_skill():
    return CitizenshipResources()
