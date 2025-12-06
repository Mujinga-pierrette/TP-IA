"""
ASPIRATEUR : agent réflexe simple qui nettoie deux chambres toutes les 2 minutes.
Usage: python aspirateur.py
Cliquez sur une chambre pour la rendre sale (test).
Modifier CLEAN_INTERVAL pour accélérer les tests (par défaut 120 secondes).
"""
import pygame
import sys
import time

# -------- Configuration --------
WINDOW_W, WINDOW_H = 720, 360
ROOM_W, ROOM_H = 260, 220
ROOM_A_POS = (40, 60)
ROOM_B_POS = (400, 60)

AGENT_RADIUS = 14
AGENT_SPEED = 180.0  # pixels per second

CLEAN_TIME = 1.2      # secondes de nettoyage
CLEAN_INTERVAL = 10    # secondes entre passes programmées

FPS = 60
# -------------------------------

# Couleurs
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
DIRT_COLOR = (150, 90, 30)
CLEAN_COLOR = (200, 255, 200)
ROOM_BORDER = (40, 40, 40)
AGENT_COLOR = (70, 130, 180)
AGENT_CLEAN_COLOR = (255, 180, 80)
TEXT_COLOR = (30, 30, 30)

# Initialisation pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("ASPIRATEUR – Agent réflexe simple")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22)
bigfont = pygame.font.SysFont(None, 28)

# ---------- Classes ----------
class Room:
    def __init__(self, name, topleft):
        self.name = name
        self.topleft = topleft
        self.rect = pygame.Rect(topleft[0], topleft[1], ROOM_W, ROOM_H)
        self.dirty = False

    def toggle(self):
        self.dirty = not self.dirty

class Agent:
    def __init__(self, pos):
        self.x, self.y = pos
        self.target = None
        self.state = "idle"  # idle, moving, cleaning
        self.clean_timer = 0.0

    def set_target(self, pos):
        self.target = pos
        self.state = "moving"

    def update(self, dt):
        if self.state == "moving" and self.target:
            tx, ty = self.target
            dx = tx - self.x
            dy = ty - self.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            step = AGENT_SPEED * dt

            if dist <= step:
                self.x, self.y = tx, ty
                self.state = "idle"
                self.target = None
            else:
                self.x += dx / dist * step
                self.y += dy / dist * step

        elif self.state == "cleaning":
            self.clean_timer -= dt
            if self.clean_timer <= 0:
                self.state = "idle"

    def start_cleaning(self, duration):
        self.state = "cleaning"
        self.clean_timer = duration

# ---------- Initialisation ----------
roomA = Room("Chambre A", ROOM_A_POS)
roomB = Room("Chambre B", ROOM_B_POS)

agent = Agent((ROOM_A_POS[0] + ROOM_W // 2, ROOM_A_POS[1] + ROOM_H + 40))

# Gestion de séquence
sequence = {
    "active": False,
    "queue": [],
    "step": 0,
    "phase": "move"
}

def start_sequence(visit_queue):
    if sequence["active"]:
        return
    sequence["active"] = True
    sequence["queue"] = visit_queue.copy()
    sequence["step"] = 0
    sequence["phase"] = "move"

    first = sequence["queue"][0]
    agent.set_target(first.rect.center)

def update_sequence(dt):
    if not sequence["active"]:
        return

    if sequence["phase"] == "move":
        if agent.state == "idle":
            current_room = sequence["queue"][sequence["step"]]
            if current_room.dirty:
                agent.start_cleaning(CLEAN_TIME)
                current_room.dirty = False
            sequence["phase"] = "clean"

    elif sequence["phase"] == "clean":
        if agent.state == "idle":
            sequence["step"] += 1
            if sequence["step"] >= len(sequence["queue"]):
                sequence["active"] = False
            else:
                next_room = sequence["queue"][sequence["step"]]
                agent.set_target(next_room.rect.center)
                sequence["phase"] = "move"

def reflex_decision_and_act():
    visit_queue = []
    if roomA.dirty and roomB.dirty:
        visit_queue = [roomA, roomB]
    elif roomA.dirty:
        visit_queue = [roomA]
    elif roomB.dirty:
        visit_queue = [roomB]
    else:
        return
    start_sequence(visit_queue)

# ---------- Affichage ----------
def draw_room(room):
    bg = DIRT_COLOR if room.dirty else CLEAN_COLOR
    pygame.draw.rect(screen, bg, room.rect)
    pygame.draw.rect(screen, ROOM_BORDER, room.rect, 3)

    # Nom
    label = bigfont.render(room.name, True, TEXT_COLOR)
    screen.blit(label, (room.rect.x + 10, room.rect.y + 10))

    # Statut
    status = "SALE" if room.dirty else "PROPRE"
    color = DIRT_COLOR if room.dirty else (0, 120, 0)
    st = font.render(status, True, color)
    screen.blit(st, (room.rect.x + 10, room.rect.y + 40))

def draw_agent():
    color = AGENT_CLEAN_COLOR if agent.state == "cleaning" else AGENT_COLOR
    pygame.draw.circle(screen, color, (int(agent.x), int(agent.y)), AGENT_RADIUS)

    txt = font.render("ASPIRATEUR", True, TEXT_COLOR)
    screen.blit(txt, (agent.x - 40, agent.y - AGENT_RADIUS - 24))

    state_txt = font.render(f"État : {agent.state}", True, TEXT_COLOR)
    screen.blit(state_txt, (10, WINDOW_H - 30))

def draw_instructions():
    lines = [
        "Cliquez sur une chambre pour la salir.",
        f"Passes automatiques toutes les {CLEAN_INTERVAL} secondes.",
        "Règle : si A et B sales -> nettoie A puis B."
    ]
    for i, line in enumerate(lines):
        txt = font.render(line, True, TEXT_COLOR)
        screen.blit(txt, (10, WINDOW_H - 100 + i * 20))

def draw_next_pass_time(next_time):
    now = time.time()
    remain = max(0, int(next_time - now))
    t = f"Prochaine passe dans : {remain}s"
    txt = font.render(t, True, TEXT_COLOR)
    screen.blit(txt, (WINDOW_W - 260, WINDOW_H - 30))

# ---------- Boucle principale ----------
def main_loop():
    global last_pass_time
    running = True
    last_pass_time = time.time()

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if roomA.rect.collidepoint(mx, my):
                    roomA.toggle()
                elif roomB.rect.collidepoint(mx, my):
                    roomB.toggle()

        # Vérifie si l’intervalle de nettoyage est écoulé
        now = time.time()
        if now - last_pass_time >= CLEAN_INTERVAL:
            reflex_decision_and_act()
            last_pass_time = now

        # Mises à jour
        agent.update(dt)
        update_sequence(dt)

        # Affichage
        screen.fill(WHITE)
        draw_room(roomA)
        draw_room(roomB)
        draw_agent()
        draw_instructions()
        draw_next_pass_time(last_pass_time + CLEAN_INTERVAL)

        if sequence["active"]:
            s = "Séquence active : " + " -> ".join(
                [r.name for r in sequence["queue"][sequence["step"]:]]
            )
            txt = font.render(s, True, TEXT_COLOR)
            screen.blit(txt, (10, WINDOW_H - 70))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

# ---------- Lancer le programme ----------
if __name__ == "__main__":
    main_loop()

()