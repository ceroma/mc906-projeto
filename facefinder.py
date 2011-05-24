from facebook import *
from facelector import *
from eigenfaces import *
import cv, os, sys
import threading, random

def save_image_face(image_file, square, folder = '.'):
  x, y, w, h = square
  image = Image.open(image_file)
  face = image.crop((x, y, x + w, y + h)).resize((100, 100)).convert("L")
  face.save(folder + '/' + image_file)

# Constants:
FACES_DIR = 'faces'
PICTS_DIR = 'pictures'
HAARS_DIR = 'haarcascades'
EIGEN_TOP_PCT = 0.75
MAX_CLOSEST_CLASSES = 6
FACELECTOR_OUTPUT = 'target.jpg'
HAAR_CASCADE_NAME = 'haarcascade_frontalface_alt.xml'

# Usage:
if len(sys.argv) < 2:
  print "Usage: python facefinder.py input_image"
  sys.exit()

# Prepare working directory:
print "Initializing..."
FF_DIR = os.path.abspath(os.curdir)
if FACES_DIR not in os.listdir('.'):
  os.mkdir(FACES_DIR)
if PICTS_DIR not in os.listdir('.'):
  os.mkdir(PICTS_DIR)

# Launch face selector:
print "Launching Face Selector..."
facelector_args = (sys.argv[1], os.path.join(FF_DIR, FACELECTOR_OUTPUT))
threading.Thread(target = facelector, args = facelector_args).start()

# Get user's friends of friends:
print "Fetching friends of friends..."
friends = get_user_friends()
fofs = friends # get_users_friends(friends)
fofs = random.sample(friends, 30)

# Get users' profile pictures:
print "Fetching users' pictures..."
os.chdir(PICTS_DIR)
save_users_pictures(fofs, size = 'large')
while (threading.activeCount() > 1):
  time.sleep(1)

# Find faces in users' profile pictures:
print "Finding users' faces..."
cascade = cv.Load(os.path.join(FF_DIR, HAARS_DIR, HAAR_CASCADE_NAME))
for file in os.listdir('.'):
  image = cv.LoadImageM(file, cv.CV_LOAD_IMAGE_GRAYSCALE)
  faces = cv.HaarDetectObjects( \
    image, cascade, cv.CreateMemStorage(0), scale_factor = 1.2, \
    min_neighbors = 2, flags = 0, min_size = (20, 20))
  if len(faces) >= 1:
    save_image_face(file, faces[0][0], folder = os.path.join(FF_DIR, FACES_DIR))

# Calculate eigenfaces:
print "Calculating Face Space..."
os.chdir(os.path.join(FF_DIR, FACES_DIR))
faces_files = os.listdir('.')
average_face = get_average_face(faces_files)
w, u = get_eigenfaces(average_face, faces_files)
eigenvalues, eigenfaces = get_top_eigenfaces(w, u, EIGEN_TOP_PCT)
classes = get_images_classes(average_face, eigenfaces, faces_files)

# Wait for the face to be chosen by the face selector:
print "Waiting for Face Selector..."
os.chdir(FF_DIR)
while (FACELECTOR_OUTPUT not in os.listdir('.')):
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
