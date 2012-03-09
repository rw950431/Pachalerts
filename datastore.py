#!/usr/bin/env python

from google.appengine.ext import db

class Trigger(db.Model):
    user=db.IMProperty(required=True)
    trigger=db.StringProperty(required=True)
    desc=db.StringProperty()
    last_trigger=db.DateTimeProperty()
    last_notify=db.DateTimeProperty()
    paused=db.BooleanProperty()



