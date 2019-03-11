largura = 480
altura = 600
fps = 60
titulo = 'Jumpy Joe!'
font_nome = 'arial'
MS_FILE = "score.txt"
SPRITSHEET = "spritesheet_jumper.png"

white = (255, 255, 255)
black = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
LIGHTBLUE = (50, 200, 255)
BGCOLOR = LIGHTBLUE

# Plataformas iniciais
PLATFORM_LIST = [(10, altura-50), (180, altura-50),  # (350, altura-50),
                 (largura/2-50, altura*3/4),
                 (80, altura-350),
                 (350, 200),
                 (175, 100)]

# propriedades do player
PLAYER_ACC = 0.7
PLAYER_FRICTION = -0.12
GRAVIDADE = 0.5
PLAYER_JUMP = 16

# Propriedades do jogo
BOOST_POWER = 40
POW_FREQ = 6  # %
# MOB_FREQ = 9000  # ms
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 2
MOB_LAYER = 2
CLOUD_LAYER = 0
