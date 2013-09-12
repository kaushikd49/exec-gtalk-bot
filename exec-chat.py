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

    def command_100_default(self, user, message, args):
        '''.*?(?s)(?m)'''
        try:
            ldap = self.validate_user_and_get_ldap(user.getStripped())
            custom_message = "hey! watsup %s? I'm a bot" % ldap
            self.replyMessage(user, custom_message)
        except ValildationException as excp:
            self.replyMessage(user, excp.message)
        except Exception as excp:
            msg =  "Something went wrong %s " % excp.message
            self.print_and_reply(excp, msg, user)

    def parse_user_auth_config(self):
        config_file_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        print "dir is " , os.path.dirname(__file__), CONFIG_FILE
        conf = ConfigObj('%s' % config_file_path)
        self.auth_data = conf

    def print_and_reply(self, excp, msg, user):
        print(msg)
        self.replyMessage(user, excp.message)

    def validate_user_and_get_ldap(self, user_mail_id):
        suffix = '@flipkart.com'
        if not user_mail_id.endswith(suffix):
            raise ValildationException("You are not part of flipkart. Im afraid you cant execute any commands!")
        print "validated %s" % user_mail_id
        return user_mail_id[:-len(suffix)]

    def validate_grammar(request):
        pass


if __name__ == "__main__":
    bot = SampleBot()
    bot.setState('available', "Simple Gtalk Robot")
    bot.start("ks.kshk@gmail.com", "nomorehackkano")