#!/usr/bin/env python

from google.appengine.ext import db

class Trigger(db.Model):
    """ One entry for each trigger definition """
    user=db.IMProperty(required=True)
    trigger=db.StringProperty(required=True)
    desc=db.StringProperty()
    last_trigger=db.DateTimeProperty()
    last_notify=db.DateTimeProperty()
    paused=db.BooleanProperty()

class Statistics(db.Model):
    """ Persistant storage of overall app performance """
    users=db.IntegerProperty() #total users
    triggers=db.IntegerProperty() #number of posts to /trigger
    notifies=db.IntegerProperty() #number of XMPP notifies sent
    probes=db.IntegerProperty() #count requests to non-handled URLS
    chats=db.IntegerProperty() #count XMPP user interactions
    row_total=db.IntegerProperty() #count total rows stored in db




