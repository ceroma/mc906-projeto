import json
import pickle
import urllib2

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
  # Request profile picture:
  pic = urllib2.urlopen(graph + user + '/picture?type=' + size)

  # Save picture:
  f = open(user + '.jpg', 'w')
  f.write(pic.read())

def save_users_pictures(user_ids, size = 'large'):
  for uid in user_ids:
    save_user_picture(uid, size)

fofs = get_users_friends(get_user_friends()[])
print len(fofs)
pickle.dump(fofs, open("fofs.pck", "w"))
