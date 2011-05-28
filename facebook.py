import json, os
import urllib, urllib2
import threading, time

max_threads = 200
graph = 'https://graph.facebook.com/'
access_token = # Get access token the hacky way by going to
               # http://developers.facebook.com/docs/reference/api/ 

def batch_request(request):
  # Make batch request:
  args = {'access_token' : access_token, 'batch' : json.dumps(request)}
  return json.loads(urllib2.urlopen(graph, urllib.urlencode(args)).read())

def get_user_connections(user = 'me', type = 'friends', filter = None):
  # Request connections:
  try:
    data = json.loads( \
             urllib2.urlopen( \
               graph + user + '/' + type + '?access_token=' + access_token \
             ).read() \
           )
  except:
    data = {u'data': []}

  # Filter response:
  if filter:
    return [connection[filter] for connection in data[u'data']]
  else:
    return data[u'data']

def get_user_friends(user = 'me'):
  return get_user_connections(user, type = 'friends', filter = 'id')

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

def get_photo(source, timeout = 10):
  try:
    # Request source file:
    photo = urllib2.urlopen(source)
    return photo
  except:
    if timeout > 0:
      get_photo(source, timeout = timeout - 1)
    else:
      return None

def get_user_picture(user = 'me', size = 'large'):
  # Request profile picture:
  return get_photo(graph + user + '/picture?type=' + size)

def save_user_picture(user = 'me', size = 'large', path = '.'):
  # Get picture and save on disk:
  pic = get_user_picture(user, size)
  if pic:
    f = open(os.path.join(path, user + '.jpg'), 'w')
    f.write(pic.read())
    f.close()

def save_users_pictures(user_ids, size = 'large', path = '.'):
  # Start threads to download pictures:
  for uid in user_ids:
    while threading.activeCount() > max_threads:
      time.sleep(1)
    args = (uid, size, path)
    threading.Thread(target = save_user_picture, args = args).start()

def get_user_tags(user = 'me'):
  # Request tagged photos:
  photos = get_user_connections(user, type = 'photos')

  # Get image source and user tag for each photo:
  tags = []
  for photo in photos:
    source = photo['source']
    for tag_data in photo['tags']['data']:
      if tag_data['id'] == user:
        tag_x = int(tag_data['x'] * photo['width'] / 100)
        tag_y = int(tag_data['y'] * photo['height'] / 100)
        break
    tags.append((source, (tag_x, tag_y)))

  return tags
