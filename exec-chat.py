#!/usr/bin/python

import sys
import pysftp
import os
import re
import traceback

from configobj import ConfigObj
from PyGtalkRobot import GtalkRobot
from collections import defaultdict

RESPONSE_CHAR_LIMIT = 2048

RUN_ONLY_ON = 'run_only_on'
REGISTER = 'register'
CONFIG_FILE = 'config/auth_config.ini'


# Common utils
class Common:
    @staticmethod
    def log_error(msg=''):
        print traceback.format_exc(msg + " " + traceback.format_exc())

    @staticmethod
    def get_sub_dict(dict,keys):
        return dict((k, dict[k]) for k in keys)

# Common Validation exception
class ValildationException(Exception):
    pass

# SSH login exception
class SSHException(Exception):
    pass

class SSHCommandExecException(Exception):
    pass

# Responsible for login and maintaining state
class SSHLoginPool:
    user_login_dict = defaultdict(dict)

    def ssh(self, ldap, machines):
        print("machines ", machines)
        for m in machines:
            self.login_and_update(ldap,m)
        return self.user_login_dict

    def login_and_update(self, ldap, host_machine):
        try:
            if not self.is_host_registered(host_machine, ldap):
                print("Attempting logging into %s " % host_machine)
                con = pysftp.Connection(host_machine)
                print("Logged into %s " % host_machine)
                self.user_login_dict[ldap][host_machine] = con
        except:
            Common.log_error("Error while trying to ssh to %s" % host_machine)
            raise SSHException()

    def is_host_registered(self, host_machine, ldap):
        return ldap in self.user_login_dict and host_machine in self.user_login_dict[ldap]

    def get_pool(self):
        return self.user_login_dict

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
# Bug - run_only_at  and register and run
class CommandParseAndExecutor:
    def __init__(self, ssh_pool):
        self.ssh_provider_pool = ssh_pool

    # TODO
    def execute(self, ldap, message):
        result = self.validate_grammar_and_get_res(ldap, message)
        resp = self.prepare_response(result)
        # message = "hey! watsup %s? I'm a bot " % ldap
        return resp

    def run_cmd(self, ldap, hosts, message):
        user_login_dict = self.ssh_provider_pool.get_pool()
        all_registerd_hosts = (hosts if hosts else user_login_dict[ldap].keys())
        if not all_registerd_hosts:
            raise ValildationException("register host(s) before running commands or use %s (m1,m2) cmd " % RUN_ONLY_ON)
        return self.run_cmd_on_machines(ldap, user_login_dict, all_registerd_hosts, message)

    def validate_grammar_and_get_res(self, ldap, message):
        if re.match('%s.*' % REGISTER, message):         # register host machines
            host_machines = self.get_machines_for_registration_only(message)
            self.ssh_provider_pool.ssh(ldap, host_machines)
            return "done registering ...."
        elif re.match('%s.*' % RUN_ONLY_ON, message):                    # run cmd on a specific set of hosts # TODO
            host_machine, command = self.get_machines_for_single_run(message)
            self.ssh_provider_pool.ssh(ldap, [host_machine])
            return self.run_cmd(ldap, [host_machine], command) # particular host
        else:
            print "executing..."
            return self.run_cmd(ldap, [], message) # all hosts

    def get_machines_for_single_run(self, message):
        substr = re.split(RUN_ONLY_ON, message)[1:][0]   # 'run_only_on erp-inv-app1 ls /' => 'erp-inv-app1 ls /'
        return substr.strip().split(' ',1)    # ['erp-inv-app1', 'ls /']


    def get_machines_for_registration_only(self, message):
        # print "message is %s " % message
        array_with_machine_str = re.split(REGISTER,message)[1:]  # ['m1 m2']
        # print("array_with_machine_str %s" % array_with_machine_str)
        machine_list = array_with_machine_str[0].strip().split(' ') # m1, m2
        if not machine_list:
            raise ValildationException("Correct way to register machines: % m1 m2", REGISTER)
        return machine_list

    def run_cmd_on_machines(self, ldap, user_login_dict, host_machines, command):
        res = {}
        try:
            for host in host_machines:
                self.ssh_provider_pool.is_host_registered(host,ldap)
                ssh_conn = user_login_dict[ldap][host]
                res[host] = ssh_conn.execute(command)
        except SSHCommandExecException:
            Common.log_error("Failure while runnign ssh command")
            raise
        return res


    def surround_with(self, str, border_strs="*" * 20):
        pretty_resp = "%s %s %s" % (border_strs, str, border_strs)
        return pretty_resp

    def prepare_response(self, result):
        if not isinstance(result,str):
            res = ["\n"]
            for key,val in result.items():
                funky_key = self.surround_with(key) + "\n"
                concat_val = ''.join(val)
                host_resp = self.surround_with(concat_val, funky_key)
                res.append(host_resp)
            return "\n".join(res)
        return result

# Central Facade
class CommandExecBot(GtalkRobot):
    ldap_provider = LdapProvider()
    command_executor = CommandParseAndExecutor(SSHLoginPool())

    def command_100_default(self, user, message, args):
        '''.*''' # handle all messages like a boss
        self.listen_to_chat(user, message, args)

    def listen_to_chat(self, user, message, args):
        try:
            ldap = self.ldap_provider.get_ldap(user.getStripped())
            response = self.command_executor.execute(ldap, message.strip())
            self.replyMessage(user, response[:RESPONSE_CHAR_LIMIT])
        except (ValildationException, SSHException) as e:
            self.replyMessage(user, e.message)
        except:
            Common.log_error("Exception in listen_to_chat:")
            self.replyMessage(user, "Something went wrong")



if __name__ == "__main__":
    bot = CommandExecBot()
    bot.setState('available', "Simple Gtalk Robot")
    bot.start("ks.kshk@gmail.com", "nomorehackkano")