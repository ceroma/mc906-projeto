import json
import pickle
import urllib
import urllib2
import threading
import time

max_threads = 200
graph = 'https://graph.facebook.com/'
access_token = # Get access token the hacky way by going to
               # http://developers.facebook.com/docs/reference/api/ 

def batch_request(request):
  # Make batch request:
  args = {'access_token' : access_token, 'batch' : json.dumps(request)}
  return json.loads(urllib2.urlopen(graph, urllib.urlencode(args)).read())

def get_user_connections(user = 'me', type = 'friends'):
  # Request connections:
  try:
    data = json.loads( \
             urllib2.urlopen( \
               graph + user + '/' + type + '?access_token=' + access_token \
             ).read() \
           )
  except:
    data = {u'data': []}

  # Filter IDs:
  return [connection[u'id'] for connection in data[u'data']]

def get_user_friends(user = 'me'):
  return get_user_connections(user, type = 'friends')

def get_users_friends(user_ids):
  # Create batch request:
  response = {}
  i = 0
  while (i < len(user_ids)):
    data = batch_request( \
      [{"method": "GET", \
        "relative_url": uid + '/friends'} for uid in user_ids[i:i+20]] \
      )

    # Save user friends:
    for user in data:
      if user['code'] == 200:
        for friend in json.loads(user['body'])['data']:
          response[friend['id']] = friend['id']
    i = i + 20

  return response

def save_user_picture(user = 'me', size = 'large', timeout = 10):
  try:
    # Request profile picture:
    pic = urllib2.urlopen(graph + user + '/picture?type=' + size)
  
    # Save picture:
    f = open(user + '.jpg', 'w')
    f.write(pic.read())
  except:
    timeout -= 1
    if timeout > 0:
      save_user_picture(user, size, timeout = timeout)

def save_users_pictures(user_ids, size = 'large'):
  # Start threads to download pictures
  for uid in user_ids:
    while threading.activeCount() > max_threads:
      time.sleep(1)
    threading.Thread(target = save_user_picture, args = (uid, size)).start()
