import pygame
import sys, os
import webbrowser

def facelector(image_name, output_name = 'target.jpg', faces = []):
  # Open picture and initialize screen:
  pygame.display.init()
  photo = pygame.image.load(image_name)
  screen = pygame.display.set_mode(photo.get_size())
  pygame.display.set_caption("Face Selector")

  # Blit photo to the screen:
  screen.blit(photo, (0,0))
  pygame.display.flip()

  # Initialize rectangles:
  selected_face = None
  faces = [pygame.Rect(face) for face in faces]

  # Events loop:
  clock = pygame.time.Clock()
  while True:
    clock.tick(60)

    # Handle events:
    pygame.event.pump()
    key_state = pygame.key.get_pressed()
    if key_state[pygame.K_ESCAPE] or pygame.event.peek(pygame.QUIT):
      pygame.display.quit()
      return

    # Handle mouse hovering - highlight faces:
    x, y = pygame.mouse.get_pos()
    for face in faces:
      if face.collidepoint(x, y):
        selected_face = face
        break
    else:
      selected_face = None

    # Handle mouse clicks - crop selected face:
    mouse_state = pygame.mouse.get_pressed()
    if mouse_state[0] and selected_face:
      face = pygame.Surface(selected_face.size)
      face.blit(photo, (0,0), selected_face)
      pygame.image.save(face, output_name)
      pygame.display.quit()
      return

    # Draw everything:
    screen.blit(photo, (0, 0))
    for face in faces:
      pygame.draw.rect(screen, (255, 0, 0), face, 3)
    if selected_face:
      pygame.draw.rect(screen, (0, 255, 0), selected_face, 3)
    pygame.display.flip()

def facelector_manual(image_name, output_name = 'target.jpg'):
  # Constants:
  RESIZING_TOP = 1
  RESIZING_LEFT = 2
  RESIZING_RIGHT = 3
  RESIZING_BOTTOM = 4

  # Open picture and initialize screen:
  pygame.display.init()
  photo = pygame.image.load(image_name)
  screen = pygame.display.set_mode(photo.get_size())
  pygame.display.set_caption("Face Selector")

  # Blit photo to the screen:
  screen.blit(photo, (0,0))
  pygame.display.flip()

  # Initialize target box:
  moving_target = False
  resizing_target = False
  target = pygame.Rect(0, 0, 100, 100)
  target.center = (photo.get_width()/2, photo.get_height()/2)

  # Events loop:
  clock = pygame.time.Clock()
  while True:
    clock.tick(60)

    # Handle events:
    pygame.event.pump()
    key_state = pygame.key.get_pressed()
    if key_state[pygame.K_ESCAPE] or pygame.event.peek(pygame.QUIT):
      pygame.display.quit()
      return

    # Enter - crop target box: 
    if key_state[pygame.K_RETURN]:
      face = pygame.Surface(target.size)
      face.blit(photo, (0,0), target)
      pygame.image.save(face, output_name)
      pygame.display.quit()
      return

    # Handle mouse clicks - move and resize target box:
    mouse_state = pygame.mouse.get_pressed()
    if mouse_state[0]:
      x, y = pygame.mouse.get_pos()
      if moving_target:
        target.center = (x, y)
      elif resizing_target:
        if resizing_target == RESIZING_TOP:
          delta = y - target.top
          target.top += delta
          target.left += delta
          target.width -= delta
          target.height -= delta
        elif resizing_target == RESIZING_LEFT:
          delta = x - target.left
          target.top += delta
          target.left += delta
          target.width -= delta
          target.height -= delta
        elif resizing_target == RESIZING_RIGHT:
          delta = x - target.right
          target.width += delta
          target.height += delta
        elif resizing_target == RESIZING_BOTTOM:
          delta = y - target.bottom
          target.width += delta
          target.height += delta
      elif (y >= target.top - 5) and (y <= target.top + 5) and \
           (x >= target.left) and (x <= target.right):
        resizing_target = RESIZING_TOP
      elif (x >= target.left - 5) and (x <= target.left + 5) and \
           (y >= target.top) and (y <= target.bottom):
        resizing_target = RESIZING_LEFT
      elif (x >= target.right - 5) and (x <= target.right + 5) and \
           (y >= target.top) and (y <= target.bottom):
        resizing_target = RESIZING_RIGHT
      elif (y >= target.bottom - 5) and (y <= target.bottom + 5) and \
           (x >= target.left) and (x <= target.right):
        resizing_target = RESIZING_BOTTOM
      else:
        moving_target = True
    else:
      moving_target = False
      resizing_target = False

    # Draw everything:
    screen.blit(photo, (0,0))
    pygame.draw.rect(screen, (255, 0, 0), target, 3)
    pygame.display.flip()

def profile_selector(user_ids, images_path = '.'):
  # Constants:
  BORDER = 10
  UID, PHOTO, RECT = range(3)
  PROFILE_URL = 'https://www.facebook.com/profile.php?id='

  # Open profile pictures:
  pygame.display.init()
  profiles = []
  screen_width, screen_height = BORDER, 2 * BORDER
  for uid in user_ids:
    photo = pygame.image.load(os.path.join(images_path, uid + '.jpg'))
    profiles.append([uid, photo])
    screen_width += photo.get_width() + BORDER
    screen_height = max(screen_height, photo.get_height() + 2 * BORDER)

  # Initialize screen:
  pygame.display.set_caption("Profile Selector")
  screen = pygame.display.set_mode((screen_width, screen_height))
  background = pygame.Surface(screen.get_size())
  background.fill((250, 250, 250))
  screen.blit(background, (0, 0))

  # Blit profile pictures to the screen:
  left, centery = BORDER, screen_height / 2
  for profile in profiles:
    rect = profile[PHOTO].get_rect()
    rect.left, rect.centery = left, centery
    profile.append(rect)
    screen.blit(profile[PHOTO], rect)
    left += profile[PHOTO].get_width() + BORDER
  pygame.display.flip()

  # Events loop:
  selected_profile = None
  clock = pygame.time.Clock()
  while True:
    clock.tick(60)

    # Handle events:
    pygame.event.pump()
    key_state = pygame.key.get_pressed()
    if key_state[pygame.K_ESCAPE] or pygame.event.peek(pygame.QUIT):
      pygame.display.quit()
      return

    # Handle mouse hovering - highlight profiles:
    x, y = pygame.mouse.get_pos()
    for profile in profiles:
      if profile[RECT].collidepoint(x, y):
        selected_profile = profile
        break
    else:
      selected_profile = None

    # Handle mouse clicks - open selected profile:
    mouse_state = pygame.mouse.get_pressed()
    if mouse_state[0] and selected_profile:
      webbrowser.open(PROFILE_URL + selected_profile[UID])
      pygame.display.quit()
      return

    # Draw everything:
    screen.blit(background, (0, 0))
    for profile in profiles:
      screen.blit(profile[PHOTO], profile[RECT])
    if selected_profile:
      pygame.draw.rect(screen, (255, 0, 0), selected_profile[RECT], 3)
    pygame.display.flip()
