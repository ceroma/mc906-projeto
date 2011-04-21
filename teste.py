import json
import pickle
import urllib
import urllib2
import threading
import time

graph = 'https://graph.facebook.com/'
access_token = '2227470867|2.ijPpUMki73Ffx2MsKU_16w__.3600.1303412400.0-647275296|5ZeIJS9qmF8KjYGXYm9c23ip2oI'
max_retry = 200

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

def save_user_picture(user = 'ceroma', size = 'large', timeout = 10):
  try:
    # Request profile picture:
    pic = urllib2.urlopen(graph + user + '/picture?type=' + size)
  
    # Save picture:
    f = open(user + '.jpg', 'w')
    f.write(pic.read())
  except:
    timeout -= 1
    print "Timeout %d para user %s" %(timeout, user)
    save_user_picture(user, timeout = timeout)

def save_users_pictures(user_ids, size = 'large'):
  for uid in user_ids:
    while threading.activeCount() > max_retry:
      time.sleep(1)
    threading.Thread(target = save_user_picture, args = (uid, )).start()

def batch_request(request):
  args = {'access_token' : access_token, 'batch' : json.dumps(request)}
  return json.loads(urllib2.urlopen(graph, urllib.urlencode(args)).read())

def get_users_friends(user_ids):
  response = {}
  i = 0
  while (i < len(user_ids)):
    request = [{"method": "GET", "relative_url": uid + '/friends'} for uid in user_ids[i:i+20]]
    data = batch_request(request)
    for user in data:
      if user['code'] == 200:
        for friend in json.loads(user['body'])['data']:
          response[friend['id']] = friend['id']
    i = i + 20

  return response
  
friends = get_user_friends()
fofs = get_users_friends(friends)
save_users_pictures(fofs.keys())
while threading.activeCount() > 1:
  print threading.activeCount()
  time.sleep(1)
pickle.dump(fofs, open("fofs.pck", "w"))
