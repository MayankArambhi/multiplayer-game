import pygame
import sys
import random
import websocket
import json
from Backend._timer import Timer as timer

# client-server connection
ws = websocket.WebSocket()
IPV4_address = input("Enter IPV4 address: ")
ws.connect(f"ws://{IPV4_address}:8000/ws")

name = input("Enter your name: ")
# send registration
ws.send(json.dumps({"name": name,
                    "keysPressed": {}
                    }))
data = ws.recv()
json_data = json.loads(data)
while name not in json_data["entities"]:
    data = ws.recv()
    json_data = json.loads(data)

health = json_data["entities"][name]["health"]
width = json_data["screenSize"]["width"]
height = json_data["screenSize"]["height"]

# pygame initialization
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# sound mixer
pygame.mixer.init()
pygame.mixer.set_num_channels(32)

bounce_channel = pygame.mixer.Channel(1)
damage_channel = pygame.mixer.Channel(2)

bounce_sound = pygame.mixer.Sound(str("Assets/bounce.wav"))
bounce_sound.set_volume(0.15)
damage_sound = pygame.mixer.Sound(str("Assets/damage.wav"))
damage_sound.set_volume(0.3)
pygame.mixer.music.load(str("Assets/bg.wav"))
# pygame.mixer.music.play(-1)  # -1 = infinite loop

# twinkling star background
def generate_stars(w,h):
    x,y = random.randint(1,w),random.randint(1,h)
    return x,y
stars = []
for i in range(100):
    stars.append(generate_stars(width,height))

pygame.display.set_caption("Survive The Balls")

while True:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    # clear screen
    screen.fill((0, 0, 0))
    for star in stars:
        pygame.draw.circle(screen, (255,255,255), star, random.choice([1,1,1,2,3]))

    keyPressed = {
        "up": False,
        "down": False,
        "left": False,
        "right": False,
        "restart": False
    }

    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        keyPressed["up"] = True

    if keys[pygame.K_DOWN]:
        keyPressed["down"] = True

    if keys[pygame.K_RIGHT]:
        keyPressed["right"] = True

    if keys[pygame.K_LEFT]:
        keyPressed["left"] = True

    if keys[pygame.K_r]:
        keyPressed["restart"] = True

    json_data = json.loads(data)
    while name not in json_data["entities"]:
        data = ws.recv()
    ws.send(json.dumps({"name": name, "keysPressed": keyPressed}))
    data = ws.recv()
    json_data = json.loads(data)
    health = json_data["entities"][name]["health"]
    status = json_data["entities"][name]["status"]

    if status == "Dead":
        font = pygame.font.SysFont(None, 40)
        count_text = font.render(f"Game Over", True, (255, 0, 0))
        text_rect = count_text.get_rect(center=(width//2, height//2))
        screen.blit(count_text, text_rect)

        font = pygame.font.SysFont(None, 25)
        count_text = font.render(f"Press R to restart", True, (255, 255, 255))
        text_rect = count_text.get_rect(center=(width//2, height//2+30))
        screen.blit(count_text, text_rect)

    else:
        t = timer()
        t.start()
            
        # draw ball
        t.stop()
        font = pygame.font.SysFont(None, 20)
        count_text = font.render(f"Ping: {int(float(t.__str__()) * 1000)}ms", True, (255, 255, 255))
        text_rect = count_text.get_rect(topleft=(10,10))
        screen.blit(count_text, text_rect)
        for connectionName in json_data["entities"].keys():
            font = pygame.font.SysFont(None, 20)
            if connectionName == name:
                pygame.draw.circle(
                    screen,
                    (50, 50, 150),
                    (json_data["entities"][connectionName]["pos_x"], json_data["entities"][connectionName]["pos_y"]),
                    20
                )
                count_text = font.render(f"You", True, (255, 255, 255))
                text_rect = count_text.get_rect(center=(json_data["entities"][connectionName]["pos_x"], json_data["entities"][connectionName]["pos_y"]+30))
                screen.blit(count_text, text_rect)
                if json_data["entities"][connectionName]["status"] == "Knife equipped":
                    font = pygame.font.SysFont("Segoe UI Emoji", 32)
                    count_text = font.render(f"🔪", True, (255, 255, 255))
                    text_rect = count_text.get_rect(center=(json_data["objects"]["Knife"]["pos_x"], json_data["objects"]["Knife"]["pos_y"]))
                    screen.blit(count_text, text_rect)
            else:
                if json_data["entities"][connectionName]["status"] == "Dead":
                    continue
                pygame.draw.circle(
                    screen,
                    (150, 0, 0),
                    (json_data["entities"][connectionName]["pos_x"], json_data["entities"][connectionName]["pos_y"]),
                    20
                )
                count_text = font.render(f"{connectionName}", True, (255, 255, 255))
                text_rect = count_text.get_rect(center=(json_data["entities"][connectionName]["pos_x"], json_data["entities"][connectionName]["pos_y"]+30))
                screen.blit(count_text, text_rect)
                if json_data["entities"][connectionName]["status"] == "Knife equipped":
                    font = pygame.font.SysFont("Segoe UI Emoji", 32)
                    count_text = font.render(f"🔪", True, (255, 255, 255))
                    text_rect = count_text.get_rect(center=(json_data["objects"]["Knife"]["pos_x"], json_data["objects"]["Knife"]["pos_y"]))
                    screen.blit(count_text, text_rect)
            if json_data["entities"][connectionName]["event"] == "Damage received":
                damage_channel.play(damage_sound)

        for objName in json_data["objects"].keys():
            if not json_data["objects"][objName]["isTaken"]:
                font = pygame.font.SysFont("Segoe UI Emoji", 32)
                count_text = font.render(f"🔪", True, (255, 255, 255))
                text_rect = count_text.get_rect(center=(json_data["objects"][objName]["pos_x"], json_data["objects"][objName]["pos_y"]))
                screen.blit(count_text, text_rect)

        margin = 10
        font = pygame.font.SysFont("Segoe UI Emoji", 16)
        for entity in json_data["entities"]:
            if entity == name:
                count_text = font.render(f"{entity}: {json_data["entities"][entity]["health"] * "💖"}", True, (255, 255, 255))
            else:
                count_text = font.render(f"{entity}: {json_data["entities"][entity]["health"] * "💖"}", True, (255, 0, 0))
            text_rect = count_text.get_rect(topright=(width - 10, margin))
            screen.blit(count_text, text_rect)
            margin += 15

    pygame.display.flip()
    clock.tick(60)