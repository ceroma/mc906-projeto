import json
import pickle
import urllib
import urllib2
import threading
import time

graph = 'https://graph.facebook.com/'
access_token = # Get access token the hacky way by going to 
               # http://developers.facebook.com/docs/reference/api/ 

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

def get_user_groups(user = 'me'):
  return get_user_connections(user, type = 'groups')

def get_users_connections(user_ids, connection_getter):
  ids = {}
  for user in user_ids:
    for id in connection_getter(user):
      ids[id] = id
  return ids

def get_users_friends(user_ids):
  return get_users_connections(user_ids, get_user_friends)

def get_users_groups(user_ids):
  return get_users_connections(user_ids, get_user_groups)

def save_user_picture(user = 'ceroma', size = 'large'):
  try:
    # Request profile picture:
    pic = urllib2.urlopen(graph + user + '/picture?type=' + size)
  
    # Save picture:
    f = open(user + '.jpg', 'w')
    f.write(pic.read())
  except:
    save_user_picture(user)

def save_users_pictures(user_ids, size = 'large'):
  for uid in user_ids:
    args = (uid, )
    if threading.activeCount() > 200:
      time.sleep(1)
    threading.Thread(target = save_user_picture, args = args).start()

def batch_request(user_ids):
  response = []
  request = []
  for uid in user_ids:
    request.append({"method": "GET", "relative_url": uid + '/friends'})

    if len(request) == 20:
      args = {}
      args['access_token'] = access_token
      args['batch'] = json.dumps(request)
      data = json.loads(urllib2.urlopen(graph, urllib.urlencode(args)).read())
      for user in data:
        if user['code'] == 200:
          for friendId in json.loads(user['body'])['data']:
            response.append(friendId['id'])
      request = []
        
  return response
  
friends = get_user_friends()
fofs = batch_request(friends)
save_users_pictures(fofs)
while threading.activeCount() > 1:
  time.sleep(1)
pickle.dump(fofs, open("fofs.pck", "w"))
