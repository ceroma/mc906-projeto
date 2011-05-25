from numpy import *
from PIL import Image

DIM = 10000
WIDTH, HEIGHT = 100, 100

def get_average_face(image_files):
  # Calculate average face:
  average = zeros((HEIGHT, WIDTH))
  for image_file in image_files:
    image = asarray(Image.open(image_file))
    average += image
  average = average / len(image_files)

  return average

def get_eigenfaces(average_face, image_files):
  # Initialize first line:
  diff_face = asarray(Image.open(image_files[0])) - average_face
  diffs_matrix_t = diff_face.reshape(1, DIM)

  # Complete matrix t(A):
  for image_file in image_files[1:]:
    diff_face = asarray(Image.open(image_file)) - average_face
    diffs_matrix_t = concatenate((diffs_matrix_t, diff_face.reshape(1, DIM)))

  # Calculate v, eigenvectors of t(A)*A:
  diffs_matrix = diffs_matrix_t.transpose()
  w, v = linalg.eig(dot(diffs_matrix_t, diffs_matrix))

  # Eigenface i, eigenvector of A*t(A), is A*vi:
  u = dot(diffs_matrix, v)
  for i in range(u.shape[1]):
    u[:,i] = u[:,i] / linalg.norm(u[:,i])

  return w, u

def get_top_eigenfaces(eigenvalues, eigenvectors, pct_or_n):
  # Sort eigenvalues in decreasing order:
  idx_sort = argsort(eigenvalues)[::-1]

  # Top N eigenvectors:
  if (pct_or_n >= 1):
    top_n = pct_or_n

  # Top eigenvectors that account for pct% variance:
  else:
    i, cvalues = 0, 0.0
    values_sum = sum(eigenvalues)
    while ((cvalues / values_sum) < pct_or_n):
      cvalues += eigenvalues[idx_sort[i]]
      i += 1
    top_n = i

  return eigenvalues[idx_sort[:top_n]], eigenvectors[:,idx_sort[:top_n]]

def get_image_class(average_face, eigenfaces, image_file):
  # Calculate image's class:
  image_class = []
  diff_image = asarray(Image.open(image_file)) - average_face
  diff_image = diff_image.reshape(1, DIM)
  for k in range(eigenfaces.shape[1]):
    image_class.append(sum(eigenfaces[:,k].transpose() * diff_image))

  return image_class

def get_images_classes(average_face, eigenfaces, image_files):
  # Build dict with all classes:
  classes = {}
  for image_file in image_files:
    classes[image_file[:-4]] = \
      get_image_class(average_face, eigenfaces, image_file)

  return classes

def get_image_distances(average_face, eigenfaces, classes, image_file):
  # Project image in face space:
  target = get_image_class(average_face, eigenfaces, image_file)

  # Calculate distance to classes:
  dists = {}
  for classe in classes:
    dists[classe] = linalg.norm(array(target) - array(classes[classe]))

  # Calculate distance to face space:
  diff_image = asarray(Image.open(image_file)) - average_face
  proj_image = zeros((1, DIM))
  for i in range(eigenfaces.shape[1]):
    proj_image += target[i] * eigenfaces[:,i]
  space_dist = linalg.norm(diff_image.reshape(1, DIM) - proj_image)

  return space_dist, dists

def find_image_class(average_face, eigenfaces, classes, image_file):
  # Find closest class:
  space, dists = \
    get_image_distances(average_face, eigenfaces, classes, image_file)
  min_class, min_dist = dists.keys()[0], dists[dists.keys()[0]]
  for classe in dists.keys()[1:]:
    if dists[classe] < min_dist:
      min_class, min_dist = classe, dists[classe]

  return min_class
