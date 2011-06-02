from facebook import *
from facelector import *
from eigenfaces import *
from PIL import ImageOps
import cv, os, sys
import pickle, threading, random

# Constants:
FACES_DIR = 'faces'
PICTS_DIR = 'pictures'
TRAIN_DIR = 'training'
HAARS_DIR = 'haarcascades'
MAX_THREADS = 20
EIGEN_TOP_PCT = 0.75
MAX_CLOSEST_CLASSES = 6
FACELECTOR_OUTPUT = 'target.jpg'
EIGENFACES_PICKLE = 'eigenfaces.pck'
HAAR_CASCADE_NAME = 'haarcascade_frontalface_alt.xml'

def detect_image_faces(image_file, cascade):
  # Detect all faces in image:
  try:
    image = cv.LoadImageM(image_file, cv.CV_LOAD_IMAGE_GRAYSCALE)
    faces = cv.HaarDetectObjects( \
      image, cascade, cv.CreateMemStorage(0), scale_factor = 1.2, \
      min_neighbors = 2, flags = 0, min_size = (20, 20))
  except:
    faces = []

  return faces

def crop_image_face(input_file, output_file, square, resize = (WIDTH, HEIGHT)):
  # Open image and adjust rectangle:
  image = Image.open(input_file)
  x, y, w, h = square
  x, y = max(x, 0), max(y, 0)
  w, h = min(w, image.size[0] - x), min(h, image.size[1] - y)

  # Crop image:
  face = image.crop((x, y, x + w, y + h))
  if resize:
    face = face.resize(resize).convert("L")
    face = ImageOps.equalize(face)
  face.save(output_file)

def crop_tagged_photo(user_id, source, tag, size = 200):
  # Get original photo:
  pic = get_photo(source)
  file_name = os.path.join(PICTS_DIR, user_id + '.jpg')
  if pic:
    f = open(file_name, 'w')
    f.write(pic.read())
    f.close()

  # Crop photo around tag:
  tag_x, tag_y = tag
  square = (tag_x - size/2, tag_y - size/2, size, size)
  crop_image_face(file_name, file_name, square, resize = None)

def save_user_face(user_id, cascade):
  # Check if user face is already present:
  user_image = user_id + '.jpg'
  if user_image in os.listdir(FACES_DIR):
    return

  # Get user picture if not present:
  if user_image not in os.listdir(PICTS_DIR):
    save_user_picture(user_id, path = PICTS_DIR)

  # Find the user's face:
  retry_count, retry_max = 0, 5
  face_file = os.path.join(FACES_DIR, user_image)
  picture_file = os.path.join(PICTS_DIR, user_image)
  while retry_count < retry_max:
    if user_image in os.listdir(PICTS_DIR):
      # Try to find face on current picture:
      faces = detect_image_faces(picture_file, cascade)
      if len(faces) >= 1:
        crop_image_face(picture_file, face_file, faces[0][0])
        break

      # Not found on profile picture, get tagged photos:
      if retry_count == 0:
        tags = get_user_tags(user_id)
        retry_max = min(retry_max, len(tags))

      # Update current picture:
      if tags:
        source, tag = random.choice(tags)
        crop_tagged_photo(user_id, source, tag)
    retry_count = retry_count + 1

# Command line execution:
if __name__ == '__main__':
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
  cascade = cv.Load(os.path.join(FF_PATH, HAARS_DIR, HAAR_CASCADE_NAME))
  faces = [face for face, nb in detect_image_faces(sys.argv[1], cascade)]
  facelector_args = [sys.argv[1], os.path.join(FF_PATH, FACELECTOR_OUTPUT)]
  if faces:
    facelector_args.append(faces)
    facelector_thread = \
      threading.Thread(target = facelector, args = facelector_args)
  else:
    facelector_thread = \
    threading.Thread(target = facelector_manual, args = facelector_args)
  facelector_thread.start()

  # Get user's friends of friends:
  print "Fetching friends of friends..."
  friends = get_user_friends()
  fofs = get_users_friends(friends)

  # Fetch profile pictures and find users' faces:
  print "Fetching pictures and finding faces..."
  for user_id in fofs:
    while (threading.activeCount() > MAX_THREADS):
      time.sleep(1)
    threading.Thread(target = save_user_face, args = (user_id, cascade)).start()
  while (threading.activeCount() > 2 or \
        (threading.activeCount() == 2 and not facelector_thread.isAlive())):
    time.sleep(1)

  # Calculate eigenfaces:
  if EIGENFACES_PICKLE in os.listdir(os.curdir):
    print "Loading Face Space..."
    average_face, eigenfaces = pickle.load(open(EIGENFACES_PICKLE, 'r'))
  else:
    print "Calculating Face Space..."
    if TRAIN_DIR in os.listdir(os.curdir):
      training_files = \
        [os.path.join(TRAIN_DIR, file) for file in os.listdir(TRAIN_DIR)]
    else:
      training_files = \
        [os.path.join(FACES_DIR, file) for file in os.listdir(FACES_DIR)]
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
  target = target.resize((WIDTH, HEIGHT)).convert("L")
  target = ImageOps.equalize(target).save(FACELECTOR_OUTPUT)

  # Calculate distances to face-space and classes:
  print "Searching chosen face..."
  space_dist, classes_dists = \
    get_image_distances(average_face, eigenfaces, classes, FACELECTOR_OUTPUT)
  os.remove(FACELECTOR_OUTPUT)

  # Return closest classes:
  print "Done.\n\nClosest faces:"
  closest_uids = []
  closest_classes = sorted(classes_dists.items(), key = lambda x: x[1])
  for uid, dist in closest_classes[:MAX_CLOSEST_CLASSES]:
    closest_uids.append(uid)
    print str(dist) + ' - ' + uid
  profile_selector(closest_uids, PICTS_DIR)

  # Save average face and eigenfaces:
  if EIGENFACES_PICKLE not in os.listdir(os.curdir):
    print "\nSaving Face Space.."
    pickle.dump((average_face, eigenfaces), open(EIGENFACES_PICKLE, 'w'))
