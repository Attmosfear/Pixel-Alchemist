import pygame

pygame.init()

screen = pygame.display.set_mode((480, 320))
pygame.display.set_caption('Pixel Alchemist')
running = True
screen.fill((255, 255, 255))

player = pygame.image.load('Assets/Art/playerTest.png').convert()

clock = pygame.time.Clock()

player_position_x = 240
player_position_y = 160


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_LEFT]:
        player_position_x -= 1
    if pressed[pygame.K_RIGHT]:
        player_position_x += 1
    if pressed[pygame.K_UP]:
        player_position_y -= 1
    if pressed[pygame.K_DOWN]:
        player_position_y += 1

    screen.fill((255, 255, 255))
    screen.blit(player, (player_position_x, player_position_y))
    pygame.display.flip()
    clock.tick(120)
pygame.quit()