import os
import sys
import random
import pygame as pg

class JogoDaMemoria:
    def __init__(self):
        pg.init()  # Inicia o Pygame
        pg.mixer.init() 

        self.clock = pg.time.Clock()

        self.base_path = os.path.dirname(os.path.abspath(__file__))  # Caminho da pasta do script

        # Carregar música de fundo
        self.background_music = "dont_fail.mp3"
        pg.mixer.music.load(self.background_music)
        pg.mixer.music.set_volume(0.3)  # Define o volume da música (0.0 a 1.0)
        pg.mixer.music.play(-1, 0.0)  # Começa a música em loop

        # Carregar sons adicionais
        self.flip_sound = pg.mixer.Sound(os.path.join(self.base_path, "virar_carta.wav"))
        self.success_sound = pg.mixer.Sound(os.path.join(self.base_path, "acerto_carta.wav"))
        self.whistle_sound = pg.mixer.Sound(os.path.join(self.base_path, "som_apito.mp3"))
        self.error_sound = pg.mixer.Sound(os.path.join(self.base_path, "erro.mp3"))

        # Cores
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.green_light = (100, 255, 100)
        self.black = (0, 0, 0)

        # Janela
        self.window = pg.display.set_mode((1100, 900))
        pg.display.set_caption("Jogo da Memória")

        # Fonte
        self.font = pg.font.SysFont(None, 48)

        # Estado do jogo
        self.state = "start"
        self.cards = [['#'] * 5 for _ in range(4)]
        self.cards_map = [[''] * 5 for _ in range(4)]
        self.cards_in_play = []
        self.waiting = False
        self.delay_timer = 0
        self.shuffle_cards = True
        self.restart_option = False
        self.last_left_click = False

        # Carrega recursos
        self.load_images()

    def load_images(self):
        def load_image(name):
            path = os.path.join(self.base_path, name)
            try:
                return pg.transform.scale(pg.image.load(path), (100, 100))
            except FileNotFoundError:
                print(f"Imagem não encontrada: {path}")
                return pg.Surface((100, 100))

        try:
            path_down = os.path.join(self.base_path, 'carta_para_baixo.png')
            self.card_down = pg.transform.scale(pg.image.load(path_down), (150, 150))
        except FileNotFoundError:
            print(f"Erro: '{path_down}' não encontrada.")
            self.card_down = pg.Surface((150, 150))

        try:
            path_up = os.path.join(self.base_path, 'carta_para_cima.png')
            self.card_up = pg.transform.scale(pg.image.load(path_up), (150, 150))
        except FileNotFoundError:
            print(f"Erro: '{path_up}' não encontrada.")
            self.card_up = pg.Surface((150, 150))

        self.images = {
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
        }

    def clear_window(self):
        self.window.fill(self.black)  # Essa parte muda o fundo do jogo

    def blit_card(self, card, x, y):
        card_x = 50 + (x * 200)
        card_y = 50 + (y * 200)

        if card == '#':
            self.window.blit(self.card_down, (card_x, card_y))
        elif card == '':  # Caso a carta esteja vazia
            pass
        else:
            self.window.blit(self.card_up, (card_x, card_y))
            img = self.images.get(card)
            if img:
                self.window.blit(img, (card_x + 25, card_y + 25))

    def board(self):
        for y in range(4):
            for x in range(5):
                self.blit_card(self.cards[y][x], x, y)

    def shuffling_cards(self):
        if self.shuffle_cards:
            self.cards_map = [[''] * 5 for _ in range(4)]
            for card in range(20):
                placed = False
                while not placed:
                    y = random.randint(0, 3)
                    x = random.randint(0, 4)
                    if self.cards_map[y][x] == '':
                        self.cards_map[y][x] = str(card // 2)
                        placed = True
            self.shuffle_cards = False

    def card_selection(self, mouse_pos, click_just_pressed):
        if self.waiting or len(self.cards_in_play) >= 2:
            return

        for y in range(4):
            for x in range(5):
                card_x = 50 + (x * 200)
                card_y = 50 + (y * 200)

                if self.cards[y][x] == '#':
                    if card_x <= mouse_pos[0] <= card_x + 150 and card_y <= mouse_pos[1] <= card_y + 150:
                        pg.draw.rect(self.window, self.red, (card_x - 10, card_y - 10, 170, 170), 5, 15)

                        if click_just_pressed:
                            self.cards[y][x] = self.cards_map[y][x]
                            self.cards_in_play.append((x, y))
                            self.flip_sound.play()  # Tocar som de virada de carta
                            return

    def card_combinations(self):
        if len(self.cards_in_play) == 2 and not self.waiting:
            self.delay_timer = pg.time.get_ticks()
            self.waiting = True

        if self.waiting and pg.time.get_ticks() - self.delay_timer >= 1000:
            x1, y1 = self.cards_in_play[0]
            x2, y2 = self.cards_in_play[1]

            if self.cards_map[y1][x1] == self.cards_map[y2][x2]:
                self.cards[y1][x1] = ''
                self.cards[y2][x2] = ''
                self.success_sound.play()  # Tocar som de acerto
            else:
                self.cards[y1][x1] = '#'
                self.cards[y2][x2] = '#'
                self.error_sound.play()  # Som de erro adicionado

            self.cards_in_play = []
            self.waiting = False

    def end_of_game(self):
        if not self.restart_option:
            if all(self.cards[y][x] == '' for y in range(4) for x in range(5)):
                self.restart_option = True

    def restart_game(self):
        self.cards = [['#'] * 5 for _ in range(4)]
        self.cards_map = [[''] * 5 for _ in range(4)]
        self.restart_option = False
        self.shuffle_cards = True
        self.cards_in_play = []
        self.waiting = False

    def restart_button(self, mouse):
        if self.restart_option:
            text = self.font.render("Restart", True, self.black)
            width, height = text.get_size()
            box_width = width + 100
            box_height = height + 100
            box_x = (self.window.get_width() - box_width) // 2
            box_y = (self.window.get_height() - box_height) // 2

            hovered = box_x <= mouse[0][0] <= box_x + box_width and box_y <= mouse[0][1] <= box_y + box_height
            color = self.green_light if hovered else self.green

            pg.draw.rect(self.window, color, (box_x, box_y, box_width, box_height))
            pg.draw.rect(self.window, self.black, (box_x, box_y, box_width, box_height), 5)
            self.window.blit(text, ((self.window.get_width() - width) // 2, (self.window.get_height() - height) // 2))

            if hovered and mouse[2][0]:
                self.restart_game()

    def start_screen(self, mouse, click):
        self.clear_window()
        title = self.font.render("Jogo da Memória", True, self.white)
        button = self.font.render("Jogar", True, self.black)

        button_w, button_h = 300, 100
        button_x = (self.window.get_width() - button_w) // 2
        button_y = 500

        hovered = button_x <= mouse[0] <= button_x + button_w and button_y <= mouse[1] <= button_y + button_h
        color = self.green_light if hovered else self.green

        pg.draw.rect(self.window, color, (button_x, button_y, button_w, button_h))
        pg.draw.rect(self.window, self.black, (button_x, button_y, button_w, button_h), 5)
        self.window.blit(title, ((self.window.get_width() - title.get_width()) // 2, 200))
        self.window.blit(button, ((self.window.get_width() - button.get_width()) // 2, button_y + 25))

        if hovered and click:
            self.whistle_sound.play()  # Tocar o som do apito
            self.state = "playing"
            self.restart_game()


if __name__ == "__main__":
    jogo = JogoDaMemoria()

    while True:
        jogo.clock.tick(60)

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.mixer.music.stop()  # Para a música ao sair
                pg.quit()
                sys.exit()

        mouse_pos = pg.mouse.get_pos()
        mouse_input = pg.mouse.get_pressed()
        left_click = mouse_input[0]
        click_just_pressed = left_click and not jogo.last_left_click
        jogo.last_left_click = left_click

        if jogo.state == "start":
            jogo.start_screen(mouse_pos, click_just_pressed)
        else:
            jogo.clear_window()
            jogo.shuffling_cards()
            jogo.board()
            jogo.card_selection(mouse_pos, click_just_pressed)
            jogo.card_combinations()
            jogo.end_of_game()
            jogo.restart_button((mouse_pos, mouse_input, (click_just_pressed, False, False)))

        pg.display.update()
