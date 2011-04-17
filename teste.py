import json
import urllib2

graph = 'https://graph.facebook.com/'
access_token = # Get access token the hacky way by going to 
               # http://developers.facebook.com/docs/reference/api/ 

def get_user_connections(user = 'me', type = 'friends'):
  # Request connections:
  data = json.loads( \
           urllib2.urlopen( \
             graph + user + '/' + type + '?access_token=' + access_token \
           ).read() \
         )

  # Filter IDs:
  return [connection[u'id'] for connection in data[u'data']]

def get_user_friends(user = 'me'):
  return get_user_connections(user, type = 'friends')

def get_user_groups(user = 'me'):
  return get_user_connections(user, type = 'groups')

def get_users_groups(user_ids):
  gids = {}
  for user in user_ids:
    for gid in get_user_groups(user):
      gids[gid] = gid
  return gids

def save_user_picture(user = 'ceroma', size = 'large'):
  # Request profile picture:
  pic = urllib2.urlopen(graph + user + '/picture?type=' + size)

  # Save picture:
  f = open(user + '.jpg', 'w')
  f.write(pic.read())

def save_users_pictures(user_ids, size = 'large'):
  for uid in user_ids:
    save_user_picture(uid, size)

print save_users_pictures(get_user_friends())
