exec-gtalk-bot
==============

A Gtalk bot that supports running remote ssh commands.

## How does it work ?
This tool uses PyGtalkRobot to bring up an instance of GtalkBot. 
This instace responds to certain commands, to help run remote ssh commands via pysftp.

##Usage

- Install the following Python modules
   * pysftp
   * py3dns
   * xmpppy
   * configobj 
- Update the following details in config/auth_config.ini

gmail_bot_email_id=<gtalk-bot-email_id>
gmail_bot_password=<gtalk-bot-password>


[<user1-email-id-goes-here>]
    username=<username-for-ssh-login-to-target-machine>
    password=<password-for-ssh-login-to-target-machine>
[<user2-email-id-goes-here>]
    username=<username-for-ssh-login-to-target-machine>
    password=<password-for-ssh-login-to-target-machine>
..


- Add the user <gtalk-bot-email_id> and start chatting 
- Run: python exec-chat.py


Please find some sample usage/output in the wiki





