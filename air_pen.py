import serial
import pygame

# ✅ PORT
PORT = '/dev/tty.usbserial-5B151671991'
ser = serial.Serial(PORT, 115200, timeout=1)

# ✅ INIT
pygame.init()
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SLD Air Writing")

font = pygame.font.SysFont("Arial", 300)

# Letters
letters = ["A", "B", "C", "D"]
current_index = 0

def draw_letter():
    screen.fill((255, 255, 255))
    letter_surface = font.render(letters[current_index], True, (200, 200, 200))
    rect = letter_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(letter_surface, rect)

draw_letter()

# start position
prev_x, prev_y = WIDTH//2, HEIGHT//2

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 🔥 CONTROLS
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                draw_letter()

            if event.key == pygame.K_n:
                current_index = (current_index + 1) % len(letters)
                draw_letter()

    try:
        data = ser.readline().decode().strip()

        if data:
            print("DATA:", data)

            parts = data.split(',')

            x_val = int(parts[0].split(':')[1])
            y_val = int(parts[1].split(':')[1])

            # 🔥 SCALE (reduce sensitivity)
            x = int((x_val / 20000) * WIDTH)
            y = int((y_val / 20000) * HEIGHT)

            # limit inside screen
            x = max(0, min(WIDTH, x))
            y = max(0, min(HEIGHT, y))

            # 🔥 STRONG SMOOTHING
            alpha = 0.1
            x = int(prev_x + alpha * (x - prev_x))
            y = int(prev_y + alpha * (y - prev_y))

            # 🔥 DEAD ZONE (remove noise)
            if abs(x - prev_x) < 5 and abs(y - prev_y) < 5:
                x, y = prev_x, prev_y

            # 🔥 LIMIT SPEED (control movement)
            max_step = 15
            dx = x - prev_x
            dy = y - prev_y

            if abs(dx) > max_step:
                x = prev_x + max_step * (1 if dx > 0 else -1)

            if abs(dy) > max_step:
                y = prev_y + max_step * (1 if dy > 0 else -1)

            # 🔥 DRAW SMOOTH LINE
            pygame.draw.line(screen, (0, 0, 0), (prev_x, prev_y), (x, y), 4)

            prev_x, prev_y = x, y

    except Exception as e:
        print("Error:", e)

    pygame.display.update()

pygame.quit()