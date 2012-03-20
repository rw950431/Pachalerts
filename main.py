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

import logging
import datetime
import time
from google.appengine.api import xmpp
#from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#from google.appengine.ext.webapp import util
from bottle import Bottle, run,static_file
from datastore import Trigger, Statistics
from google.appengine.ext import db

NOTIFY_INTERVAL=datetime.timedelta(hours=8)
#NOTIFY_INTERVAL=datetime.timedelta(minutes=2)

if not Statistics.all().get():
  #create the record to hold the stats
  n=Statistics() 
  n.users=1
  n.triggers=0
  n.notifies=0
  n.probes=0
  n.chats=0
  n.row_total=0
  n.put()
#

app = Bottle()

                      
#http://bottlepy.org/docs/stable/tutorial.html#request-routing
@app.route('/')
def index():
  return static_file('index.html',root=".")

@app.route('/robots.txt')
def robots():
  return static_file('robots.txt',root=".")

#app isnt meant to return anything for GETs
#error 405 generated when calling http://<url>/trigger/:trigger
@app.error(404)
@app.error(405)
def error404(error):
  n=Statistics.all().get()
  n.probes+=1
  n.put()
  return ''

# curl -d "some data" http://<url>/trigger/blah 
@app.post('/trigger/:trigger')
def trigger_post(trigger='xyz'):
    """Handle POST-ed data to http://<url>/trigger/<trigger_id>"""
# save updated record and put them all at once
#http://googleappengine.blogspot.com.au/2009/06/10-things-you-probably-didnt-know-about.html
    updated=[]
    now=datetime.datetime.fromtimestamp(time.time())
    then=now-NOTIFY_INTERVAL
    n=Statistics.all().get()
    n.triggers+=1
    for result in Trigger.all().filter("trigger =",trigger):
#dont notify user more often than NOTIFY_INTERVAL
      if (result.last_notify<=then) and (not result.paused):
        logging.info("send_message: %s: %s [%s]" % (result.user.address,result.desc,trigger))
        xmpp.send_message(result.user.address, '%s [%s]' %(result.desc,trigger)  )
        result.last_notify=now
        updated.append(result)
        n.notifies+=1
    db.put(updated)
    n.put()
    return ""

def main():
    run_wsgi_app(app)



if __name__ == '__main__':
    main()
