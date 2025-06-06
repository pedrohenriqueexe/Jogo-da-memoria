import os
import sys
import random
import pygame as pg

 #Variáveis globais
clock = None
window = None
font = None
base_path = os.path.dirname(os.path.abspath(__file__))

# Sons
background_music = None
flip_sound = None
success_sound = None
whistle_sound = None
error_sound = None

# Cores
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
green_light = (100, 255, 100)
black = (0, 0, 0)

# Imagens
card_down = None
card_up = None
themes = {}
images = {}

# Estado do jogo
state = "mode_selection"
theme = "times brasileiros"

cards = [['#'] * 5 for _ in range(4)]
cards_map = [[''] * 5 for _ in range(4)]
cards_in_play = []
waiting = False
delay_timer = 0
shuffle_cards_flag = True
restart_option = False
last_left_click = False

# --- Funções ---

def load_image(name, size=(100, 100)):
    path = os.path.join(base_path, name)
    try:
        img = pg.image.load(path)
        return pg.transform.scale(img, size)
    except FileNotFoundError:
        print(f"Imagem não encontrada: {path}")
        return pg.Surface(size)

def load_assets():
    global card_down, card_up, background_music, flip_sound, success_sound, whistle_sound, error_sound, themes, images

    # Imagens das cartas para cima e para baixo
    card_down = load_image('carta_para_baixo.png', (150, 150))
    card_up = load_image('carta_para_cima.png', (150, 150))

    # Sons
    try:
        pg.mixer.music.load("dont_fail.mp3")
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1, 0.0)
    except Exception as e:
        print(f"Erro ao carregar música de fundo: {e}")

    flip_sound = load_sound("virar_carta.wav")
    success_sound = load_sound("acerto_carta.wav")
    whistle_sound = load_sound("som_apito.mp3")
    error_sound = load_sound("erro.mp3")

    # Temas com imagens
    themes = {
        'times brasileiros': {
            '0': load_image('sport.png'),
            '1': load_image('vasco.png'),
            '2': load_image('palmeiras.png'),
            '3': load_image('flamengo.png'),
            '4': load_image('santos.png'),
            '5': load_image('atletico.png'),
            '6': load_image('botafogo.png'),
            '7': load_image('bahia.png'),
            '8': load_image('nautico.png'),
            '9': load_image('santacruz.png'),
        },
        'times europeus': {
            '0': load_image('barcelona.png'),
            '1': load_image('realmadrid.png'),
            '2': load_image('inter.png'),
            '3': load_image('roma.png'),
            '4': load_image('manchester.png'),
            '5': load_image('sporting.png'),
            '6': load_image('milan.png'),
            '7': load_image('boru.png'),
            '8': load_image('psg.png'),
            '9': load_image('atleticomadrid.png'),
        }
    }

    images = themes[theme]


def load_sound(name):
    path = os.path.join(base_path, name)
    try:
        return pg.mixer.Sound(path)
    except FileNotFoundError:
        print(f"Som não encontrado: {path}")
        return None


def clear_window():
    window.fill(black)


def blit_card(card, x, y):
    card_x = 50 + (x * 200)
    card_y = 50 + (y * 200)

    if card == '#':
        window.blit(card_down, (card_x, card_y))
    elif card == '':
        pass
    else:
        window.blit(card_up, (card_x, card_y))
        img = images.get(card)
        if img:
            window.blit(img, (card_x + 25, card_y + 25))


def board():
    for y in range(4):
        for x in range(5):
            blit_card(cards[y][x], x, y)


def shuffling_cards():
    global shuffle_cards_flag, cards_map

    if shuffle_cards_flag:
        cards_map = [[''] * 5 for _ in range(4)]
        for card in range(20):
            placed = False
            while not placed:
                y = random.randint(0, 3)
                x = random.randint(0, 4)
                if cards_map[y][x] == '':
                    cards_map[y][x] = str(card // 2)
                    placed = True
        shuffle_cards_flag = False


def card_selection(mouse_pos, click_just_pressed):
    global cards_in_play, waiting

    if waiting or len(cards_in_play) >= 2:
        return

    for y in range(4):
        for x in range(5):
            card_x = 50 + (x * 200)
            card_y = 50 + (y * 200)

            if cards[y][x] == '#':
                if card_x <= mouse_pos[0] <= card_x + 150 and card_y <= mouse_pos[1] <= card_y + 150:
                    pg.draw.rect(window, red, (card_x - 10, card_y - 10, 170, 170), 5, 15)
                    if click_just_pressed:
                        cards[y][x] = cards_map[y][x]
                        cards_in_play.append((x, y))
                        if flip_sound:
                            flip_sound.play()
                        return
                    
def card_combinations():
    global waiting, delay_timer, cards_in_play

    if len(cards_in_play) == 2 and not waiting:
        delay_timer = pg.time.get_ticks()
        waiting = True

    if waiting and pg.time.get_ticks() - delay_timer >= 1000:
        x1, y1 = cards_in_play[0]
        x2, y2 = cards_in_play[1]

        if cards_map[y1][x1] == cards_map[y2][x2]:
            cards[y1][x1] = ''
            cards[y2][x2] = ''
            if success_sound:
                success_sound.play()
        else:
            cards[y1][x1] = '#'
            cards[y2][x2] = '#'
            if error_sound:
                error_sound.play()

        cards_in_play = []
        waiting = False


def end_of_game():
    global restart_option
    if not restart_option:
        if all(cards[y][x] == '' for y in range(4) for x in range(5)):
            restart_option = True
            show_congratulations()


def show_congratulations():
    window.fill(black)
    congratulations_font = pg.font.SysFont(None, 60)
    congratulations_text = congratulations_font.render(
        "Parabéns, campeão! Você acertou todas as cartas!",
        True, white
    )
    text_rect = congratulations_text.get_rect(center=(window.get_width() // 2, window.get_height() // 2))
    window.blit(congratulations_text, text_rect)
    pg.display.update()
    pg.time.delay(5000)


def restart_game():
    global cards, cards_map, restart_option, shuffle_cards_flag, cards_in_play, waiting
    cards = [['#'] * 5 for _ in range(4)]
    cards_map = [[''] * 5 for _ in range(4)]
    restart_option = False
    shuffle_cards_flag = True
    cards_in_play = []
    waiting = False


def mostrar_cartas_temporariamente():
    for y in range(4):
        for x in range(5):
            cards[y][x] = cards_map[y][x]

    clear_window()
    board()
    pg.display.update()

    pg.time.delay(3000)  # Espera 3 segundos

    for y in range(4):
        for x in range(5):
            cards[y][x] = '#'

def restart_button(mouse):
    if restart_option:
        text = font.render("Restart", True, black)
        width, height = text.get_size()
        box_width = width + 100
        box_height = height + 100
        box_x = (window.get_width() - box_width) // 2
        box_y = (window.get_height() - box_height) // 2

        hovered = box_x <= mouse[0] <= box_x + box_width and box_y <= mouse[1] <= box_y + box_height
        color = green_light if hovered else green

        pg.draw.rect(window, color, (box_x, box_y, box_width, box_height))
        pg.draw.rect(window, black, (box_x, box_y, box_width, box_height), 5)
        window.blit(text, ((window.get_width() - width) // 2, (window.get_height() - height) // 2))

        if hovered and pg.mouse.get_pressed()[0]:
            restart_game()

def start_screen(mouse, click):
    clear_window()

    title = font.render("Jogo da Memória", True, white)
    button = font.render("Jogar", True, black)

    button_w, button_h = 300, 100
    button_x = (window.get_width() - button_w) // 2
    button_y = 500

    hovered = button_x <= mouse[0] <= button_x + button_w and button_y <= mouse[1] <= button_y + button_h
    color = green_light if hovered else green

    pg.draw.rect(window, color, (button_x, button_y, button_w, button_h))
    pg.draw.rect(window, white, (button_x, button_y, button_w, button_h), 5)
    window.blit(title, ((window.get_width() - title.get_width()) // 2, 200))
    window.blit(button, ((window.get_width() - button.get_width()) // 2, button_y + 25))

    if hovered and click:
        if whistle_sound:
            whistle_sound.play()
        restart_game()
        shuffling_cards()
        mostrar_cartas_temporariamente()
        global state
        state = "playing"


def mode_selection_screen(mouse, click):
    clear_window()
    temas = list(themes.keys())
    button_w, button_h = 300, 100

    for i, tema in enumerate(temas):
        x = (window.get_width() - button_w) // 2
        y = 300 + i * 100
        hovered = x <= mouse[0] <= x + button_w and y <= mouse[1] <= y + button_h
        color = green_light if hovered else green

        pg.draw.rect(window, color, (x, y, button_w, button_h))
        pg.draw.rect(window, white, (x, y, button_w, button_h), 5)

        texto = font.render(tema.capitalize(), True, black)
        window.blit(texto, (x + (button_w - texto.get_width()) // 2, y + (button_h - texto.get_height()) // 2))

        if hovered and click:
            global theme, images, state
            theme = tema
            images = themes[tema]
            state = "start_screen"


def main():
    global clock, window, font, last_left_click

    pg.init()
    pg.mixer.init()

    window = pg.display.set_mode((1100, 900))
    pg.display.set_caption("Jogo da Memória")
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 48)

    load_assets()

    running = True
    while running:
        mouse_pos = pg.mouse.get_pos()
        mouse_buttons = pg.mouse.get_pressed()
        left_click = mouse_buttons[0]
        click_just_pressed = left_click and not last_left_click
        last_left_click = left_click

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        clear_window()

        if state == "mode_selection":
            mode_selection_screen(mouse_pos, click_just_pressed)
        elif state == "start_screen":
            start_screen(mouse_pos, click_just_pressed)
        elif state == "playing":
            shuffling_cards()
            board()
            card_selection(mouse_pos, click_just_pressed)
            card_combinations()
            end_of_game()
            restart_button(mouse_pos)

        pg.display.update()
        clock.tick(30)

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()
