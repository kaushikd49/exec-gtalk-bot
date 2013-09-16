exec-gtalk-bot
==============

A Gtalk bot that supports running remote ssh commands.
This was a hack I worked on during one of the hack-nights at work.

## How does it work ?
This tool uses PyGtalkRobot to bring up an instance of GtalkBot. 
This instace responds to certain commands, to help run remote ssh commands via pysftp.

## Usage

- Install the following Python modules
   * pysftp
   * py3dns
   * xmpppy
   * configobj 
- Update the following details in config/auth_config.ini
   * gmail_bot_email_id
   * gmail_bot_password
   * ssh username and password for each gtalk user
- Add the user <gtalk-bot-email_id> and start chatting 
- python exec-chat.py

## Sample output in wiki
