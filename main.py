#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
import datetime
import time
from google.appengine.api import xmpp
#from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#from google.appengine.ext.webapp import util
from bottle import Bottle, run,static_file
from datastore import Trigger
from google.appengine.ext import db

NOTIFY_INTERVAL=datetime.timedelta(hours=8)
#NOTIFY_INTERVAL=datetime.timedelta(minutes=2)

app = Bottle()

                      
#http://bottlepy.org/docs/stable/tutorial.html#request-routing
@app.route('/')
def index():
  return static_file('index.html',root=".")

#app isnt meant to return anything for GETs
#error 405 generated when calling http://<url>/trigger/:trigger
@app.error(404)
@app.error(405)
def error404(error):
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
    for result in Trigger.all().filter("trigger =",trigger):
#dont notify user more often than NOTIFY_INTERVAL
      if (result.last_notify<=then) and (not result.paused):
        logging.info("send_message: %s, [%s] %s" % (result.user.address,trigger,result.desc))
        xmpp.send_message(result.user.address, '%s:%s' %(trigger,result.desc)  )
        result.last_notify=now
        updated.append(result)
    db.put(updated)
    return ""

def main():
    run_wsgi_app(app)



if __name__ == '__main__':
    main()
