import pygame
import sys

def facelector(image_name):
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
  target = pygame.Rect(0, 0, 50, 50)
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
      pygame.image.save(face, "face" + image_name)
      return

    # Handle mouse clicks - move and resize target box:
    mouse_state = pygame.mouse.get_pressed()
    if mouse_state[0]:
      x, y = pygame.mouse.get_pos()
      if moving_target:
        target.center = (x, y)
      if resizing_target:
        target.width = x - target.left
        target.height = y - target.top
      elif (x >= target.right - 15) and (x <= target.right + 15) and \
           (y >= target.bottom - 15) and (y <= target.bottom + 15):
        resizing_target = True
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
