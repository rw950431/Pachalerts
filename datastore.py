#!/usr/bin/env python
"""
This file is part of Pachalerts.

Pachalerts is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pachalerts is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pachalerts.  If not, see <http://www.gnu.org/licenses/>.
"""
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




