#!/usr/bin/python

import sys
import time
import pysftp


from PyGtalkRobot import GtalkRobot

class SampleBot(GtalkRobot):
    
    def command_100_default(self, user, message, args):
        '''.*?(?s)(?m)'''
        custom_message = "hey! watsup? I'm a bot "
        self.replyMessage(user, custom_message) #time.strftime("%Y-%m-%d %a %H:%M:%S", time.gmtime()))


if __name__ == "__main__":
    bot = SampleBot()
    bot.setState('available', "Simple Gtalk Robot")
    bot.start("ks.kshk@gmail.com", "nomorehackkano")
