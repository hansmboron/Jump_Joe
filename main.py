# coding: utf-8
# Art by Kenney.nl
# Sound by Syncopika and Alexandr Zhelanov and sharesynth

# Jumpy Plataform
import pygame as pg
import random
from settings import *
from sprites import *
from os import path


class Game:
    def __init__(self):
        # inicia a janela do jogo, etc
        pg.mixer.pre_init(44100, -16, 2, 2048)
        pg.mixer.init()
        pg.init()
        self.score = 0
        self.tela = pg.display.set_mode((largura, altura))
        pg.display.set_caption(titulo)
        self.relogio = pg.time.Clock()
        self.running = True
        self.font_n = pg.font.match_font(font_nome, True)
        self.load_data()

    def load_data(self):
        # carregar imagens
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, "img")
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITSHEET))
        # nuvens
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pg.image.load(path.join(img_dir, "cloud{}.png".format(i))).convert_alpha())
        # carregar efeitos sonoros
        self.snd_dir = path.join(self.dir, "snd")
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, "jump.ogg"))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, "Powerup.ogg"))
        self.mob_sound = pg.mixer.Sound(path.join(self.snd_dir, "heli.ogg"))
        self.hit_sound = pg.mixer.Sound(path.join(self.snd_dir, "hit.ogg"))

    def new(self):
        # inicializar novo jogo
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        self.mob_timer = 0
        pg.mixer.music.load(path.join(self.snd_dir, "copycat.ogg"))
        for i in range(3):
            c = Cloud(self)
            c.rect.y += 500
        self.run()

    def updateFile(self):
        try:
            f = open('img/scores.txt', 'r')
            file = f.readlines()
            global last
            last = int(file[0])
            if last < int(self.score):
                f.close()
                file = open('img/scores.txt', 'w')
                file.write(str(self.score))
                file.close()
                return self.score
            return last
        except:
            self.score = 0

    def run(self):
        # Loop infinito
        pg.mixer.music.play(-1)
        self.playing = True
        while self.playing:
            self.relogio.tick(fps)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        self.all_sprites.update()

        # Aparecer inimigo?
        agora = pg.time.get_ticks()
        if self.score < 1000:
            self.tela.fill((135,206,250))
            self.MOB_FREQ = 12000
        elif 1000 <= self.score < 2000:
            self.tela.fill((0, 191, 255))
            self.MOB_FREQ = 10000
        elif 2000 <= self.score < 3000:
            self.tela.fill((30, 144, 255))
            self.MOB_FREQ = 8000
        elif 4000 <= self.score < 5000:
            self.tela.fill((25, 25, 200))
            self.MOB_FREQ = 6000
        else:
            self.tela.fill((30, 130, 220))
            self.MOB_FREQ = 4500
        if agora - self.mob_timer > self.MOB_FREQ + choice([-2000, 0, 2000, 4000]):
            self.mob_sound.play()
            self.mob_timer = agora
            Mob(self)

        # Colidir com inimigo?
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits:
            pg.mixer.music.stop()
            self.mob_sound.stop()
            self.hit_sound.play()
            pg.time.delay(400)
            self.playing = False

        # checar se player bate em uma plataforma - apenas caindo
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False, pg.sprite.collide_mask)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if lowest.rect.right + 8 > self.player.pos.x > lowest.rect.left - 8:
                    if self.player.pos.y < lowest.rect.bottom:
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0.3
                        self.player.jumping = False

        # checar se player cai da tela
        if self.player.rect.top > altura:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.top < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            pg.mixer.music.stop()
            self.mob_sound.stop()
            self.hit_sound.play()
            pg.time.delay(300)
            self.playing = False

        # se player atingir 3/4 da altura da tela
        if self.player.rect.top <= altura / 3.5:
            if randrange(100) < 4:
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= altura:
                    plat.kill()
                    self.score += 10

        # se player pegar powerups
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == "boost":
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False

        # randomizar novas plataformas, mantendo mesmo numero de existentes
        while len(self.platforms) < 8:
            lar = random.randrange(50, 100)
            Platform(self, random.randrange(0, largura-lar),
                     random.randrange(-75, -30))

    def pause(self):
        pg.mixer.music.pause()
        self.mob_sound.stop()
        paused = True
        while paused:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_p:
                        pg.mixer.music.unpause()
                        paused = False
        pg.display.update()
        self.relogio.tick(7)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE or event.key == pg.K_UP:
                    self.player.jump()
                elif event.key == pg.K_p:
                    self.draw_text('Pausado[P]', 60, RED, largura / 2, altura / 2 - 50)
                    pg.display.update()
                    self.pause()
                elif event.key == pg.K_m:
                    pg.mixer.music.fadeout(500)
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE or event.key == pg.K_UP:
                    self.player.jump_cut()

    def draw(self):
        self.all_sprites.draw(self.tela)
        self.draw_text('Pontos: ' + str(self.score), 20, black, 70, 10)
        self.draw_text('pause[P]', 15, RED, 40, altura - 27)
        self.draw_text('Melhor Pontuação: ' + str(self.updateFile()), 16, black, largura - 100, altura - 30)
        # depois de desenhar tudo, flip the display
        pg.display.flip()

    def show_start_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, "start1.ogg"))
        bg2 = pg.image.load(path.join('img', 'bg3.png')).convert()
        pg.mixer.music.play(-1)
        self.tela.blit(bg2, (0, 0))
        # self.tela.fill(white)
        self.draw_text('JUMPY_JOE', 50, black, largura/2, altura/5)
        self.draw_text('Melhor Pontuação: ' + str(self.updateFile()), 20, black, largura/2, altura/2)
        self.draw_text('Precione alguma tecla para jogar!', 20, RED, largura/2, altura*2/3)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, "gameover.ogg"))
        bg_over = pg.image.load(path.join('img', 'game_over.png'))
        pg.mixer.music.play(-1)
        if not self.running:
            return
        # self.tela.fill(white)
        self.tela.blit(bg_over, (0, 0))
        self.draw_text('Pontos: ' + str(self.score), 20, GREEN, 70, 10)
        self.draw_text('GAME OVER', 60, RED, largura / 2, altura / 5)
        self.draw_text('Melhor Pontuação: ' + str(self.updateFile()), 20, black, largura / 2, altura / 2)
        self.draw_text('Precione alguma tecla para jogar!', 20, RED, largura / 2, altura * 2 / 3)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.relogio.tick(15)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_n, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.tela.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
quit()
