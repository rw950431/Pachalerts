#!/usr/bin/env python

#owes much to 'crowdguru'

import logging
import datetime
import time
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import xmpp_handlers

from datastore import Trigger

START_MSG = ("Now if you POST to %s/trigger/%s I will send you\n%s:%s")
STOP_MSG = ("Stopped %s OK")
PAUSE_MSG = ("Paused- send /resume %s to resume")
RESUME_MSG = ("Resumed %s")
HELP_MSG = ("Welcome to the Pachube alerts service\n"
            "To receive alerts send '/start <trigger> <description>\n"
            "eg '/start 4014 Widget counter stopped!\n"
            "To stop receiving an alert send '/stop <trigger>'\n"
            "To stop receiving all alerts send '/stop all'\n"
            "To temporarily suspend alerts send /pause <trigger> or /pause all\n"
            "Send /show to list your current alerts\n"
            )
TOO_MANY_TRIGGERS_MSG = ("There is a limit of %d triggers per user\n"
                         "please use /show and /stop to delete some existing triggers\n"
                         "before you define another one\n"
                         )
TRIGGER_LEN_MSG=("Error- please use a trigger between %d and %d characters long")
MAX_ROWS_MSG=("Sorry but the system is full, please try again later")

TRIGGER_LEN = [4,64]
DESC_LEN = [0,250]
MAX_TRIGGERS=5
MAX_ROWS=10000

def parse_user_command(message=None):
  """parse the user command into trigger id and optional description"""
  try:
    user=db.IM("xmpp",message.sender.split('/')[0])
  except AttributeError,e:
    return None,'',''

  # message.arg already has /start removed from it
  user_command=message.arg.strip()
  try:
    trigger,desc=user_command.split(' ',1)
  except ValueError,e:
    trigger=user_command
    desc=''
  return user,trigger,desc

class XmppHandler(xmpp_handlers.CommandHandler):
  """Handler class for all XMPP activity."""
  def text_message(self, message=None):
    # called if message doesnt start with /
    # Show help text
    message.reply(HELP_MSG)

  def unhandled_command(self, message=None):
    """process undefined /xxx command"""
    message.reply(HELP_MSG)

  def show_command(self, message=None):
    """process /show command"""
    # send back list of current triggers
    user,trigger,desc=parse_user_command(message)
    results_list="Current Triggers:\n"
    for result in Trigger.all().filter("user =",user):
      results_list+="%s:%s\n"%(result.trigger,result.desc)
    logging.info("show_command: %s" % (user))
    message.reply(results_list)


  def start_command(self, message=None):
    """process /start command"""
    # add to database and reply
    user,trigger,desc=parse_user_command(message)
    #total number of allowed rows
    if Trigger.all().count(MAX_ROWS) >= MAX_ROWS:
      message.reply(MAX_ROWS_MSG)
      logging.info("start_command: Max rows reached %s" % (user))
      return
    #check number of triggers user has already
    if Trigger.all().filter("user =",user).count(MAX_TRIGGERS) >= MAX_TRIGGERS:
      message.reply(TOO_MANY_TRIGGERS_MSG % MAX_TRIGGERS)
      logging.info("start_command: too many triggers %s" % (user))
      return
    #limits on trigger length
    if len(trigger)<TRIGGER_LEN[0] or len(trigger)>TRIGGER_LEN[1]:
      message.reply(TRIGGER_LEN_MSG % (TRIGGER_LEN[0],TRIGGER_LEN[1]))
      return

    result=Trigger.all().filter("user =",user).filter("trigger =",trigger).get()
    if result:
      if result.desc != desc:
        result.desc=desc
        result.put()
    else:
      new_trigger=Trigger(user=user,trigger=trigger,desc=desc)
      new_trigger.last_notify=datetime.datetime.fromtimestamp(0)
      new_trigger.paused=False
      new_trigger.put()

    logging.info("start_command: %s, [%s] %s" % (user,trigger,desc))
    message.reply(START_MSG % (self.request.host_url,trigger,trigger,desc))
    
  def stop_command(self, message=None):
    """process /stop command"""
    # message was /stop ...
    # delete from database
    user,trigger,desc=parse_user_command(message)

    if trigger.lower()=='all':
      to_be_deleted=[]
      for result in Trigger.all().filter("user =",user):
        to_be_deleted.append(result)
      db.delete(to_be_deleted)
    else:
      result=Trigger.all().filter("user =",user).filter("trigger =",trigger).get()
      if result:
        result.delete()
    logging.info("stop_command: %s, [%s]" % (user,trigger))
    message.reply(STOP_MSG % trigger )
    
  def pause_command(self, message=None):
    """process /pause command"""
    #set suspend flag
    user,trigger,desc=parse_user_command(message)
    if trigger.lower()=='all':
      to_be_paused=[]
      for result in Trigger.all().filter("user =",user).filter("paused =",False):
        result.paused=True
        to_be_paused.append(result)
      db.put(to_be_paused)
    else:
      result=Trigger.all().filter("user =",user).filter("trigger =",trigger).filter("paused =",False).get()
      if result:
        result.paused=True
        result.put()
    logging.info("pause_command: %s, [%s]" % (user,trigger))
    message.reply(PAUSE_MSG % trigger )
    
  def resume_command(self, message=None):
    """process /resume command"""
    #set suspend flag
    user,trigger,desc=parse_user_command(message)
    if trigger.lower()=='all':
      to_be_resumed=[]
      for result in Trigger.all().filter("user =",user).filter("paused =",True):
        result.paused=False
        to_be_resumed.append(result)
      db.put(to_be_resumed)
      
    else:
      result=Trigger.all().filter("user =",user).filter("trigger =",trigger).filter("paused =",True).get()
      if result:
        result.paused=False
        result.put()
    logging.info("resume_command: %s, [%s]" % (user,trigger))
    message.reply(RESUME_MSG % trigger )
    

application = webapp.WSGIApplication([
                                     ('/_ah/xmpp/message/chat/', XmppHandler)

                                     ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


