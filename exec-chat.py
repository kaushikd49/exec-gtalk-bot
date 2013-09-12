#!/usr/bin/python

import sys
import pysftp
import os

from configobj import ConfigObj
from PyGtalkRobot import GtalkRobot

CONFIG_FILE = 'config/auth_config.ini'


class ValildationException(Exception):
    pass


class SampleBot(GtalkRobot):
    auth_data = dict()

    def __init__(self):
        GtalkRobot.__init__(self)
        self.parse_user_auth_config() # update auth config
        print("auth data is ", self.auth_data.keys())

    def listen_to_chat(self, user, message, args):
        try:
            ldap = self.validate_user_and_get_ldap(user.getStripped())
            custom_message = "hey! watsup %s? I'm a bot " % ldap
            self.replyMessage(user, custom_message)
        except ValildationException as excp:
            self.replyMessage(user, excp.message)
        except:
            msg = "Something went wrong %s " % sys.exc_info()[0]
            self.print_and_reply(msg, user)

    def command_100_default(self, user, message, args):
        # '''.*?(?s)(?m)'''
        '''.*'''
        print "message insisde ", message
        self.listen_to_chat(user, message, args)

    def parse_user_auth_config(self):
        config_file_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        print "dir is " , os.path.dirname(__file__), CONFIG_FILE
        conf = ConfigObj('%s' % config_file_path)
        self.auth_data = conf

    def print_and_reply(self, msg, user):
        print(msg)
        self.replyMessage(user, msg)

    def validate_user_and_get_ldap(self, user_mail_id):
        suffix = '@flipkart.com'
        if not user_mail_id.endswith(suffix):
            raise ValildationException("You are not part of flipkart. Im afraid you cant execute any commands!")
        ldap = user_mail_id[:-len(suffix)]
        if not ldap in self.auth_data:
            raise ValildationException("No password registered for your id. Can't execute your commands :(")
        return ldap

    def validate_grammar(request):
        pass


if __name__ == "__main__":
    bot = SampleBot()
    bot.setState('available', "Simple Gtalk Robot")
    bot.start("ks.kshk@gmail.com", "nomorehackkano")