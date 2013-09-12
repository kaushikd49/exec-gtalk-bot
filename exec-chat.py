#!/usr/bin/python

import sys
import pysftp
import os
import re
import traceback

from configobj import ConfigObj
from PyGtalkRobot import GtalkRobot
from collections import defaultdict

REGISTER = 'register'

CONFIG_FILE = 'config/auth_config.ini'


# Common utils
class Common:
    @staticmethod
    def log_error(msg=''):
        print traceback.format_exc(msg + " " + traceback.format_exc())


# Common Validation exception
class ValildationException(Exception):
    pass


# Responsible for login and maintaining state
class SSHLoginPool:
    user_login_dict = defaultdict(dict)

    def login(self, ldap, machines):
        for m in machines:
            self.login_and_update(ldap,m)

    def login_and_update(self, ldap, host_machine):
        try:
            if self.is_host_registered(host_machine, ldap):
                con = pysftp.Connection(host_machine)
                self.user_login_dict[ldap].append(con)
        except:
            Common.log_error()

    def is_host_registered(self, host_machine, ldap):
        return ldap in self.user_login_dict and host_machine in self.user_login_dict[ldap]


# Validate only certain(fk) user and provide ldap.
class LdapProvider:
    auth_data = dict()

    def __init__(self):
        self.parse_user_auth_config() # update auth config
        print("auth data is ", self.auth_data.keys())

    def parse_user_auth_config(self):
        config_file_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        print "dir is " , os.path.dirname(__file__), CONFIG_FILE
        conf = ConfigObj('%s' % config_file_path)
        self.auth_data = conf

    def get_ldap(self, user_mail_id):
        suffix = '@flipkart.com'
        if not user_mail_id.endswith(suffix):
            raise ValildationException("You are not part of flipkart. Im afraid you cant execute any commands!")
        ldap = user_mail_id[:-len(suffix)]
        if not ldap in self.auth_data:
            raise ValildationException("No password registered for your id. Can't execute your commands :(")
        return ldap

# Parse, validate and exec commands
class CommandParseAndExecutor:
    def validate_grammar_and_get_res(self, ldap, message):
        if re.match('%s.*' % REGISTER, message):
            self.register_machines(ldap, self.get_machines(message))
        pass

    def get_machines(self, message):
        array_with_machine_str = re.split(REGISTER,message)[1:]  # ['m1 m2']
        machine_list = array_with_machine_str[0].strip().split('') # m1, m2
        if not machine_list:
            raise ValildationException("Correct way to register machines: % m1 m2", REGISTER)

    # TODO
    def execute(self, ldap, message):
        # self.validate_grammar_and_get_res(ldap, message)
        message = "hey! watsup %s? I'm a bot " % ldap
        return message


# Central Facade
class CommandExecBot(GtalkRobot):
    ldap_provider = LdapProvider()
    command_executor = CommandParseAndExecutor()

    def command_100_default(self, user, message, args):
        '''.*''' # handle all messages like a boss
        print "message insisde ", message
        self.listen_to_chat(user, message, args)

    def listen_to_chat(self, user, message, args):
        try:
            ldap = self.ldap_provider.get_ldap(user.getStripped())
            response = self.command_executor.execute(ldap, message.strip())
            self.replyMessage(user, response)
        except ValildationException as e:
            self.replyMessage(user, e.message)
        except:
            Common.log_error("Exception in listen_to_chat:")
            self.replyMessage(user, "Something went wrong")


if __name__ == "__main__":
    bot = CommandExecBot()
    bot.setState('available', "Simple Gtalk Robot")
    bot.start("ks.kshk@gmail.com", "nomorehackkano")