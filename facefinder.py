from facebook import *
from facelector import *
from eigenfaces import *
import cv, os, sys
import threading, random

# Constants:
FACES_DIR = 'faces'
PICTS_DIR = 'pictures'
TRAIN_DIR = 'training'
HAARS_DIR = 'haarcascades'
MAX_THREADS = 20
EIGEN_TOP_PCT = 0.75
MAX_CLOSEST_CLASSES = 6
FACELECTOR_OUTPUT = 'target.jpg'
HAAR_CASCADE_NAME = 'haarcascade_frontalface_alt.xml'

def detect_picture_face(user_id, cascade):
  user_image = os.path.join(PICTS_DIR, user_id + '.jpg')
  try:
    image = cv.LoadImageM(user_image, cv.CV_LOAD_IMAGE_GRAYSCALE)
    faces = cv.HaarDetectObjects( \
      image, cascade, cv.CreateMemStorage(0), scale_factor = 1.2, \
      min_neighbors = 2, flags = 0, min_size = (20, 20))
  except:
    faces = []

  return faces

def crop_picture_face(user_id, square):
  x, y, w, h = square
  image = Image.open(os.path.join(PICTS_DIR, user_id + '.jpg'))
  face = image.crop((x, y, x + w, y + h)).resize((100, 100)).convert("L")
  face.save(os.path.join(FACES_DIR, user_id + '.jpg'))

def save_user_face(user_id, cascade):
  # Check if user face is already present:
  user_image = user_id + '.jpg'
  if user_image in os.listdir(FACES_DIR):
    return

  # Get user picture if not present:
  if user_image not in os.listdir(PICTS_DIR):
    save_user_picture(user_id, path = PICTS_DIR)

  # Find the user's face:
  if user_image in os.listdir(PICTS_DIR):
    faces = detect_picture_face(user_id, cascade)
    if len(faces) >= 1:
      crop_picture_face(user_id, faces[0][0])

# Usage:
if len(sys.argv) < 2:
  print "Usage: python facefinder.py input_image"
  sys.exit()

# Prepare working directory:
print "Initializing..."
FF_PATH = os.path.abspath(os.curdir)
if FACES_DIR not in os.listdir(os.curdir):
  os.mkdir(FACES_DIR)
if PICTS_DIR not in os.listdir(os.curdir):
  os.mkdir(PICTS_DIR)

# Launch face selector:
print "Launching Face Selector..."
facelector_args = (sys.argv[1], os.path.join(FF_PATH, FACELECTOR_OUTPUT))
threading.Thread(target = facelector, args = facelector_args).start()

# Get user's friends of friends:
print "Fetching friends of friends..."
friends = get_user_friends()
fofs = friends # get_users_friends(friends)

# Fetch profile pictures and find users' faces:
print "Fetching pictures and finding faces..."
cascade = cv.Load(os.path.join(FF_PATH, HAARS_DIR, HAAR_CASCADE_NAME))
for user_id in fofs:
  while (threading.activeCount() > MAX_THREADS):
    time.sleep(1)
  threading.Thread(target = save_user_face, args = (user_id, cascade)).start()
while (threading.activeCount() > 2):
  time.sleep(1)

# Calculate eigenfaces:
print "Calculating Face Space..."
if TRAIN_DIR in os.listdir(os.curdir):
  training_files = [os.path.join(TRAIN_DIR, f) for f in os.listdir(TRAIN_DIR)]
else:
  training_files = [os.path.join(FACES_DIR, f) for f in os.listdir(FACES_DIR)]
average_face = get_average_face(training_files)
w, u = get_eigenfaces(average_face, training_files)
eigenvalues, eigenfaces = get_top_eigenfaces(w, u, EIGEN_TOP_PCT)

# Project users' faces to face space:
print "Projecting faces to Face Space.."
os.chdir(os.path.join(FF_PATH, FACES_DIR))
faces_files = os.listdir(os.curdir)
classes = get_images_classes(average_face, eigenfaces, faces_files)

# Wait for the face to be chosen by the face selector:
print "Waiting for Face Selector..."
os.chdir(FF_PATH)
while (FACELECTOR_OUTPUT not in os.listdir(os.curdir)):
  time.sleep(5)
target = Image.open(FACELECTOR_OUTPUT)
target = target.resize((100, 100)).convert("L").save(FACELECTOR_OUTPUT)

# Calculate distances to face-space and classes:
print "Searching chosen face..."
space_dist, classes_dists = \
  get_image_distances(average_face, eigenfaces, classes, FACELECTOR_OUTPUT)

# Return closest classes:
print "Done.\n\nClosest faces:"
closest_uids = []
closest_classes = sorted(classes_dists.items(), key = lambda x: x[1])
for uid, dist in closest_classes[:MAX_CLOSEST_CLASSES]:
  closest_uids.append(uid)
  print str(dist) + ' - ' + uid
profile_selector(closest_uids, PICTS_DIR)
