exec-gtalk-bot
==============

A Gtalk bot that supports running remote ssh commands.
This was a hack I had worked on during one of the hack-nights at work.

## How does it work ?
This hack uses PyGtalkRobot to bring up an instance of GtalkBot, which can run remote ssh commands via pysftp.

## Usage
1. Install the following Python modules
   * pysftp
   * py3dns
   * xmpppy
   * configobj 
2. Update the following details in config/auth_config.ini
   * gmail_bot_email_id
   * gmail_bot_password
   * ssh username and password for each gtalk user
3. python exec-chat.py.
4. Add the user <gtalk-bot-email_id> and start chatting. 

## Sample output in wiki
