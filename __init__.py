from mycroft import MycroftSkill, intent_file_handler
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.audio import wait_while_speaking
from mycroft.skills.context import *
from twilio.rest import Client

import time
import os
import smtplib

import socket

is_yes = lambda x: (x == "yes")
is_no = lambda x: (x == "no")

class MessageLog():
    def __init__(self, seperator='\n'):
        self._prefixes = {}
        self._suffixes = {}
        self._params = {}
        self.seperator = seperator
        self._order = []

    def add_lines(self, data=None, prefix='', suffix=''):
        if not data:
            data = {}

        self._params.update(data)
        for key in data.keys():
            self._prefixes.update({
                key: prefix
            })
            self._suffixes.update({
                key: suffix
            })
            self._order.append(key)

    def __str__(self):
        lines = [(self._prefixes[x], self._params[x], self._suffixes[x]) for x in self._order]
        return self.seperator.join(["{}{}{}".format(prefix, value, suffix) for prefix, value, suffix in lines])


class SnapResourceSkill(MycroftSkill):
    '''
        This skill has a dialogue for determining snap eligibility.

        Where can I go for more snap info?

        Am I eligible for food stamps?
    '''
    USEFUL_SNAP_LINKS = {
        'am_i_eligible': 'https://www.fns.usda.gov/snap/eligibility',
        'how_to_apply': 'https://www.fns.usda.gov/snap/apply',
        'state_information': 'https://www.fns.usda.gov/snap/snap-application-and-local-office-locators',
        'when_are_benefits_available': 'https://www.fns.usda.gov/snap/snap-monthly-benefit-issuance-schedule',
        'what_can_snap_buy': 'https://www.fns.usda.gov/snap/eligible-food-items',
        'where_can_i_use_snap_ebt': 'https://www.fns.usda.gov/snap/retailerlocator'
    }

    def __init__(self):
        MycroftSkill.__init__(self)

        socket.setdefaulttimeout(20)


        self._client = None
        self.message_log = MessageLog()

    def try_load_client(self):
        if not self.settings.get("twilio_integration_enabled"):
            return None

        if not self._client:
            if self.settings.get('twilio_account_sid') and self.settings.get('twilio_auth_token'):
                self._client = Client(self.settings.get('twilio_account_sid'), self.settings.get('twilio_auth_token'))

        return self._client


    def _collect_contact_info(self):
        if self.settings.get('twilio_integration_enabled') and self.try_load_client():
            self.record_info = self.ask_yesno('text')
        else:
            self.record_info = "no"

        self.name = "friend"
        self.phone_number = None

        if is_yes(self.record_info):
            self.speak_dialog('success')
            if self.name == "friend" or not self.phone_number:
                self.speak_dialog('intro.collect.information')
                time.sleep(3)

                if self.name == "friend":
                    self.name = self.get_response('ask.name')
                    wait_while_speaking()

                if not self.phone_number:
                    self.phone_number = self.get_response('ask.phone.number')
                    wait_while_speaking()




    @intent_file_handler('snap.list.eligibility.intent')
    def handle_snap_list(self, message):
        self.message_log = MessageLog()

        self.speak_dialog('intro.snap.eligibility')
        wait_while_speaking()

        time.sleep(3)
        detailed_inquiry = self.ask_yesno('ask.snap.eligibility.detailed')
        client = self.try_load_client()
        wait_while_speaking()

        if is_yes(detailed_inquiry):
            self._collect_contact_info()

            primary_contact_name = self.settings.get("recipient_service_worker_name")
            primary_contact_phone_number = self.settings.get("recipient_service_worker_office_phone")
            self.message_log.add_lines({ "client_name": self.name }, 'Hi ', ", this is Ezra. To get SNAP benefits, you must apply in the State in which you currently live and you must meet certain requirements, including resource and income limits.")
            self.message_log.add_lines({ "am_i_eligible": self.USEFUL_SNAP_LINKS['am_i_eligible']}, "You can visit, ", " for information on determining eligibility.")
            self.message_log.add_lines({ "state_information": self.USEFUL_SNAP_LINKS['state_information']}, "You can visit, ", " to find info on your local snap office.")
            self.message_log.add_lines({ "primary_contact_name": primary_contact_name }, "If you have questions please call your local service worker, ", "")
            self.message_log.add_lines({ "primary_contact_phone_number": primary_contact_phone_number }, "Office Phone: ", ".")

            if is_yes(self.record_info) and client and self.phone_number:
                self.speak_dialog('success')
                messageid = client.messages.create(from_=self.settings.get('twilio_from_number'), to=self.phone_number, body=str(self.message_log))
            else:
                self.speak_dialog('recite.website')

            self.speak_dialog('refer.to.primary.contact', data={'primary_contact_name': primary_contact_name, 'primary_contact_phone_number': primary_contact_phone_number})

    @intent_file_handler('snap.test.eligibility.intent')
    def handle_snap_test(self, message):
        self.message_log = MessageLog()
        self.inquire_more = False

        self.speak_dialog('intro.snap.eligibility')
        wait_while_speaking()

        time.sleep(3)
        detailed_inquiry = self.ask_yesno('ask.snap.eligibility.detailed')
        client = self.try_load_client()
        wait_while_speaking()

        if is_yes(detailed_inquiry):
            self._collect_contact_info()

            self.message_log.add_lines({ "client_name": self.name }, 'Hi ', ", this is Ezra. I'm sending along some useful information!" )

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
                        self.inquire_more = True
                        self.speak_dialog('generic.yes')
                    else:
                        self.speak_dialog('generic.no')

            if is_yes(self.record_info) and self.phone_number:
                if self.inquire_more:
                    useful_links = (
                        self.USEFUL_SNAP_LINKS['how_to_apply'],
                        self.USEFUL_SNAP_LINKS['state_information'],
                        self.USEFUL_SNAP_LINKS['what_can_snap_buy'],
                        self.USEFUL_SNAP_LINKS['where_can_i_use_snap_ebt']
                    )
                else:
                    useful_links = (
                        , self.USEFUL_SNAP_LINKS['state_information']
                    )

                data = { idx: link for idx, link in enumerate(useful_links, start=1) }
                self.message_log.add_lines(data, "- ", ",")

            if is_yes(self.record_info) and client:
                messageid = client.messages.create(from_=self.settings.get('twilio_from_number'), to=self.phone_number, body=str(self.message_log))

            if is_yes(self.record_info) and self.settings.get("send_report_on_completion"):

                email_message_log = MessageLog()
                email_message_log.add_lines({ 'introduction': self.name }, 'A new client, ', ', has inquired about Social Security Eligibility.')
                email_message_log.add_lines({ 'are_they_eligible': "" }, 'Assistance may be needed to see if they are' if self.inquire_more else 'Unfortunately they are not', ' currently eligible for the SNAP Program.')
                email_message_log.add_lines({ 'phone_number': self.phone_number }, 'An active phone number for {} is: '.format(self.name), '.')

                sender = self.settings.get("internal_communications_email")
                password = self.settings.get("internal_communications_pw")
                recepient = self.settings.get("recipient_service_worker_email")

                message_body = str(email_message_log)

                smtp_server = smtplib.SMTP_SSL('mail.tree.industries', 465)
                smtp_server.login(sender, password)
                smtp_server.sendmail(sender, recepient, message_body)
                smtp_server.close()
        else:
            self.speak_dialog('here.to.assist')
            wait_while_speaking()

def create_skill():
    return SnapResourceSkill()
