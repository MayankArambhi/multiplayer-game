import pygame
import sys
import random
import websocket
import json
from Backend._timer import Timer

# client-server connection
ws = websocket.WebSocket()
IPv4_address = input("Enter IPv4 address: ")
ws.connect(f"ws://{IPv4_address}:8000/ws")
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
borderColor = (80, 80, 100)

# pygame initialization
pygame.init()
screen = pygame.display.set_mode((width + 300, height))
clock = pygame.time.Clock()

# sound mixer
pygame.mixer.init()
pygame.mixer.set_num_channels(32)

damage_channel = pygame.mixer.Channel(2)

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

# icons
neutralPlayer = pygame.image.load("Assets/NP.png").convert_alpha()
neutralEnemy = pygame.image.load("Assets/NO.png").convert_alpha()
armedPlayer = pygame.image.load("Assets/AP.png").convert_alpha()
armedEnemy = pygame.image.load("Assets/AO.png").convert_alpha()

Knife = pygame.image.load("Assets/WN.png").convert_alpha()
Pickup = pygame.image.load("Assets/HP.png").convert_alpha()

pygame.display.set_caption("Multiplayer Fighting Game")
ping_time = 0
p = 0
chat_text = ""
saved_text = ""

typing_active = False
xhat_rect = pygame.Rect(810, 565, 200, 25)
button_rect = pygame.Rect(1020, 565, 70, 25)
textFont = pygame.font.SysFont("Tahoma", 15)
sent_text = None
updated = False

while True:
    # clear screen
    screen.fill((10,10,30))
    pygame.draw.rect(screen, (10, 0,50), (0, 0, width, height))
    pygame.draw.rect(screen, (10, 0, 50), (width + 10, 110, 280, 445))
    pygame.draw.rect(screen, borderColor, (width + 10, 110, 280, 445),1)
    pygame.draw.rect(screen, borderColor, (width, 50, 300, 1))
    pygame.draw.rect(screen, borderColor, (width, 0, 1, height))
    
    # chat
    # text block
    pygame.draw.rect(screen, borderColor, ((809), (564), 202, 27))
    pygame.draw.rect(screen, (10, 0, 50), xhat_rect)
    
    # send button
    pygame.draw.rect(screen, (150, 120, 255), (1018, 563, 74, 29))
    pygame.draw.rect(screen, (30, 6, 129), button_rect)
    
    if chat_text == "":
        text_surface = textFont.render("Type here...", True, (100,100,100))
    else:
        text_surface = textFont.render(chat_text, True, (255,255,255))
    screen.blit(text_surface, (xhat_rect.x + 4, xhat_rect.y + 3))
    send_surface = textFont.render("Send", True, (255,255,255))
    screen.blit(send_surface, send_surface.get_rect(center=button_rect.center))
    
    # typing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if xhat_rect.collidepoint(event.pos):
                typing_active = True
            else:
                typing_active = False
            if button_rect.collidepoint(event.pos):
                saved_text = chat_text
                updated = True
                chat_text = ""
        if typing_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                chat_text = chat_text[:-1]
            elif event.key == pygame.K_RETURN:
                saved_text = chat_text
                updated = True
                chat_text = ""
            else:
                chat_text += event.unicode

    # draw stars
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

    t = Timer()
    t.start()
    if updated:
        sent_text = saved_text
    ws.send(json.dumps({"name": name, "keysPressed": keyPressed, "message": sent_text}))
    sent_text = None
    updated = False
    data = ws.recv()
    t.stop()
    if ping_time >= 1:
        p = t
        ping_time = 0
    json_data = json.loads(data)
    health = json_data["entities"][name]["health"]
    status = json_data["entities"][name]["status"]

    # rendering messages
    chat = json_data["messages"]
    y = 115
    for msg in chat:
        text_surface = textFont.render(
            f"{msg['sender']}: {msg['message']}",
            True,
            (255,255,255)
        )

        screen.blit(text_surface, (width + 15, y))
        y += 20


    if status == "Dead":
        font = pygame.font.SysFont("Segoe UI", 40)
        count_text = font.render(f"Game Over", True, (255, 0, 0))
        text_rect = count_text.get_rect(center=(width//2, height//2))
        screen.blit(count_text, text_rect)

        font = pygame.font.SysFont("Segoe UI", 25)
        count_text = font.render(f"Press R to restart", True, (255, 255, 255))
        text_rect = count_text.get_rect(center=(width//2, height//2+30))
        screen.blit(count_text, text_rect)

    else:
        font = pygame.font.SysFont("Segoe UI", 20)
        count_text = font.render(f"Ping: {int(float(p.__str__()) * 1000)}ms", True, (255, 255, 255))
        text_rect = count_text.get_rect(topleft=(width + 10,8))
        screen.blit(count_text, text_rect)
        pos_x = json_data["entities"][name]["pos_x"]
        pos_y = json_data["entities"][name]["pos_y"]

        # draw balls
        if json_data["entities"][name]["status"] == "Knife equipped":
            screen.blit(
                armedPlayer,
                (pos_x - 20, pos_y - 20)
            )
        else:
            screen.blit(
            neutralPlayer,
            (pos_x - 20, pos_y - 20)
        )
        count_text = font.render(f"You", True, (255, 255, 255))
        text_rect = count_text.get_rect(center=(json_data["entities"][name]["pos_x"], json_data["entities"][name]["pos_y"]+30))
        screen.blit(count_text, text_rect)
        if json_data["entities"][name]["event"] == "Damage received":
            damage_channel.play(damage_sound)

        for connectionName in json_data["entities"].keys():
            if connectionName == name or json_data["entities"][connectionName]["status"] == "Dead":
                continue

            font = pygame.font.SysFont("Segoe UI", 20)
            pos_x = json_data["entities"][connectionName]["pos_x"]
            pos_y = json_data["entities"][connectionName]["pos_y"]
            count_text = font.render(f"{connectionName}", True, (255, 255, 255))
            text_rect = count_text.get_rect(center=(json_data["entities"][connectionName]["pos_x"], json_data["entities"][connectionName]["pos_y"]+30))
            screen.blit(count_text, text_rect)
            if json_data["entities"][connectionName]["status"] == "Knife equipped":
                screen.blit(
                    armedEnemy,
                    (pos_x - 20, pos_y - 20)
                )
            else:
                screen.blit(
                    neutralEnemy,
                    (pos_x - 20, pos_y - 20)
                )
        if json_data["entities"][connectionName]["event"] == "Damage received":
            damage_channel.play(damage_sound)

        for objName in json_data["objects"].keys():
            if not json_data["objects"][objName]["isTaken"]:
                screen.blit(
                        Knife,
                        (json_data["objects"][objName]["pos_x"] - 20, json_data["objects"][objName]["pos_y"] - 20)
                    )

        health_ico = 0
        font = pygame.font.SysFont("Segoe UI Emoji", 16)
        for i in range(json_data["entities"][name]["health"]):
            screen.blit(
                Pickup,
                (width + 10 + health_ico, 60)
            )
            health_ico += 15
    ping_time += 1/60
    pygame.display.flip()
    clock.tick(60)