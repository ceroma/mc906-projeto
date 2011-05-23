import pygame
import sys

def facelector(image_name, output_name = 'target.jpg'):
  # Constants:
  RESIZING_TOP = 1
  RESIZING_LEFT = 2
  RESIZING_RIGHT = 3
  RESIZING_BOTTOM = 4

  # Open picture and initialize screen:
  pygame.init()
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
      return

    # Enter - crop target box: 
    if key_state[pygame.K_RETURN]:
      face = pygame.Surface(target.size)
      face.blit(photo, (0,0), target)
      pygame.image.save(face, output_name)
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

# Command line execution:
if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Usage: python facelector.py image"
  else:
    facelector(sys.argv[1])
