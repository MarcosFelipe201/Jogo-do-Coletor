import pgzrun
import random
import math

# --- Configurações da Janela ---
WIDTH = 600
HEIGHT = 600
TITLE = "Pac-Maze: Arcade Edition"

# --- Matriz do Labirinto (15x15) ---
MAPA = [
    "WWWWWWWWWWWWWWW",
    "W......W......W",
    "W.WW.W.W.W.WW.W",
    " .XW.W.W.W.WX. ", 
    "W.............W",
    "W.WW.WWWWW.WW.W",
    "W....W   W....W",
    "WWWW.W   W.WWWW",
    "W....W   W....W",
    "W.WW.WWWWW.WW.W",
    "W.............W",
    "W.WW.W.W.W.WW.W",
    " .XW.W.W.W.WX. ", 
    "W......W......W",
    "WWWWWWWWWWWWWWW"
]

TAMANHO_BLOCO = 40

# --- Dificuldades ---
CONFIG_DIFICULDADE = {
    "NORMAL": {"vidas": 3, "vel_inimigo": 2, "tempo_power": 8.0, "cor": "lime"},
    "DIFICIL": {"vidas": 2, "vel_inimigo": 3, "tempo_power": 5.0, "cor": "orange"},
    "INSANO": {"vidas": 1, "vel_inimigo": 4, "tempo_power": 3.0, "cor": "red"}
}

# --- Variáveis Globais de Estado ---
modo_de_jogo = "MENU"
dificuldade = "NORMAL"
pontuacao = 0
vidas = 3
tempo_super = 0.0
tempo_animacao = 0.0

# --- Elementos do Jogo ---
paredes = []
cristais = []
super_cristais = []
inimigos = []

# --- Física e Controles do Jogador ---
jogador_rect = Rect((44, 44), (30, 30))
vel_jogador = 4
direcao_x = 0
direcao_y = 0
prox_dir_x = 0 
prox_dir_y = 0

def testar_colisao_paredes(rect_futuro):
    for parede in paredes:
        if rect_futuro.colliderect(parede):
            return True
    return False

# ==========================================
# CLASSE: Inimigo
# ==========================================
class Inimigo:
    def __init__(self, x, y, cor, dir_x, dir_y):
        self.rect = Rect((x, y), (30, 30))
        self.cor_original = cor
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.x_inicial = x
        self.y_inicial = y

    def atualizar_movimento(self, vel_atual):
        # Túnel de teletransporte
        if self.rect.right < 0: 
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH: 
            self.rect.right = 0
        
        teste_ini = self.rect.copy()
        teste_ini.x += self.dir_x * vel_atual
        teste_ini.y += self.dir_y * vel_atual
        
        if testar_colisao_paredes(teste_ini):
            opcoes = [(1,0), (-1,0), (0,1), (0,-1)]
            random.shuffle(opcoes)
            for dx, dy in opcoes:
                novo_teste = self.rect.copy()
                novo_teste.x += dx * vel_atual
                novo_teste.y += dy * vel_atual
                if not testar_colisao_paredes(novo_teste):
                    self.dir_x = dx
                    self.dir_y = dy
                    break
        else:
            self.rect.x = teste_ini.x
            self.rect.y = teste_ini.y

    def desenhar(self, tempo_super, tempo_anim):
        cor_atual = self.cor_original
        if tempo_super > 0:
            if tempo_super < 2.0 and math.sin(tempo_anim * 15) > 0:
                cor_atual = "white"
            else:
                cor_atual = "blue"
        screen.draw.filled_circle(self.rect.center, 15, cor_atual)

    def resetar_posicao(self):
        self.rect.x = self.x_inicial
        self.rect.y = self.y_inicial

# ==========================================
# LÓGICA DO JOGO
# ==========================================
def inicializar_fase():
    global direcao_x, direcao_y, prox_dir_x, prox_dir_y
    global vidas, pontuacao, tempo_super
    
    paredes.clear()
    cristais.clear()
    super_cristais.clear()
    inimigos.clear()
    
    conf = CONFIG_DIFICULDADE[dificuldade]
    pontuacao = 0
    vidas = conf["vidas"]
    tempo_super = 0.0
    
    jogador_rect.x = 45
    jogador_rect.y = 45
    direcao_x = 0; direcao_y = 0
    prox_dir_x = 0; prox_dir_y = 0
    
    for linha_idx, linha in enumerate(MAPA):
        for col_idx, caractere in enumerate(linha):
            px = col_idx * TAMANHO_BLOCO
            py = linha_idx * TAMANHO_BLOCO
            
            if caractere == "W":
                paredes.append(Rect((px, py), (TAMANHO_BLOCO, TAMANHO_BLOCO)))
            elif caractere == ".":
                cristais.append(Rect((px + 16, py + 16), (8, 8)))
            elif caractere == "X":
                super_cristais.append(Rect((px + 10, py + 10), (20, 20)))

    centro_x = 7 * TAMANHO_BLOCO + 5
    centro_y = 7 * TAMANHO_BLOCO + 5
    inimigos.append(Inimigo(centro_x, centro_y, "red", 1, 0))
    inimigos.append(Inimigo(centro_x, centro_y - TAMANHO_BLOCO, "magenta", -1, 0))
    
    if dificuldade == "INSANO":
        inimigos.append(Inimigo(centro_x, centro_y + TAMANHO_BLOCO, "orange", 0, -1))

def draw():
    screen.clear()
    
    if modo_de_jogo == "MENU":
        screen.fill((5, 5, 15))
        screen.draw.text("PAC-MAZE", center=(WIDTH//2, HEIGHT//2 - 60), fontsize=80, color="yellow", owidth=2, ocolor="blue")
        screen.draw.text("Pressione ESPAÇO para jogar", center=(WIDTH//2, HEIGHT//2 + 100), fontsize=26, color="white")
        
    elif modo_de_jogo == "DIFICULDADE":
        screen.fill((10, 10, 20))
        screen.draw.text("SELECIONE A DIFICULDADE", center=(WIDTH//2, HEIGHT//2 - 100), fontsize=50, color="white")
        screen.draw.text("[ 1 ] NORMAL (3 Vidas)", center=(WIDTH//2, HEIGHT//2 - 20), fontsize=30, color="lime")
        screen.draw.text("[ 2 ] DIFÍCIL (2 Vidas)", center=(WIDTH//2, HEIGHT//2 + 30), fontsize=30, color="orange")
        screen.draw.text("[ 3 ] INSANO (1 Vida)", center=(WIDTH//2, HEIGHT//2 + 80), fontsize=30, color="red")
        
    elif modo_de_jogo == "JOGANDO":
        screen.fill((0, 0, 0))
        for parede in paredes:
            screen.draw.rect(parede, (20, 50, 200))

        for cristal in cristais:
            screen.draw.filled_circle(cristal.center, 4, (255, 180, 150))
            
        if math.sin(tempo_animacao * 10) > 0:
            for super_c in super_cristais:
                screen.draw.filled_circle(super_c.center, 10, "gold")
            
        screen.draw.filled_circle(jogador_rect.center, 15, "yellow")
        
        for inimigo in inimigos:
            inimigo.desenhar(tempo_super, tempo_animacao)
            
        cor_dif = CONFIG_DIFICULDADE[dificuldade]["cor"]
        screen.draw.text(f"SCORE: {pontuacao}", (10, 10), fontsize=30, color="white")
        screen.draw.text(f"VIDAS: {vidas}", (WIDTH - 120, 10), fontsize=30, color="red")
        screen.draw.text(f"MODO: {dificuldade}", center=(WIDTH//2, 20), fontsize=25, color=cor_dif)
        
        if tempo_super > 0:
            screen.draw.text(f"ENERGIA: {tempo_super:.1f}s", center=(WIDTH//2, HEIGHT - 25), fontsize=35, color="cyan")

    elif modo_de_jogo == "VITORIA":
        screen.fill((0, 40, 0))
        screen.draw.text("NÍVEL CONCLUÍDO!", center=(WIDTH//2, HEIGHT//2 - 40), fontsize=60, color="lime")
        screen.draw.text(f"Score Final: {pontuacao}", center=(WIDTH//2, HEIGHT//2 + 30), fontsize=40, color="white")
        screen.draw.text("Pressione ESPAÇO para voltar ao menu", center=(WIDTH//2, HEIGHT//2 + 100), fontsize=25, color="yellow")
        
    elif modo_de_jogo == "FIM":
        screen.fill((40, 0, 0))
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2 - 40), fontsize=80, color="red")
        screen.draw.text(f"Score: {pontuacao}", center=(WIDTH//2, HEIGHT//2 + 30), fontsize=40, color="white")
        screen.draw.text("Pressione ESPAÇO para tentar de novo", center=(WIDTH//2, HEIGHT//2 + 100), fontsize=25, color="yellow")

def update(dt):
    global modo_de_jogo, pontuacao, vidas, tempo_super, tempo_animacao
    global direcao_x, direcao_y, prox_dir_x, prox_dir_y
    
    tempo_animacao += dt
    
    if modo_de_jogo != "JOGANDO":
        return

    if tempo_super > 0:
        tempo_super -= dt

    if prox_dir_x != 0 or prox_dir_y != 0:
        teste_curva = jogador_rect.copy()
        teste_curva.x += prox_dir_x * vel_jogador
        teste_curva.y += prox_dir_y * vel_jogador
        if not testar_colisao_paredes(teste_curva):
            direcao_x = prox_dir_x
            direcao_y = prox_dir_y
            prox_dir_x = 0
            prox_dir_y = 0

    if direcao_x != 0 or direcao_y != 0:
        jogador_rect.x += direcao_x * vel_jogador
        jogador_rect.y += direcao_y * vel_jogador
        if testar_colisao_paredes(jogador_rect):
            jogador_rect.x -= direcao_x * vel_jogador
            jogador_rect.y -= direcao_y * vel_jogador
            direcao_x = 0; direcao_y = 0

    if jogador_rect.right < 0:
        jogador_rect.left = WIDTH
    elif jogador_rect.left > WIDTH:
        jogador_rect.right = 0

    # Lógica de Som: Coleta de Cristal Simples
    for cristal in cristais[:]:
        if jogador_rect.colliderect(cristal):
            cristais.remove(cristal)
            pontuacao += 10
            try:
                sounds.collect_8bit.play()
                sounds.blip.play()
            except: pass

    # Lógica de Som: Coleta do Super Cristal (PowerUp)
    for super_c in super_cristais[:]:
        if jogador_rect.colliderect(super_c):
            super_cristais.remove(super_c)
            pontuacao += 50
            tempo_super = CONFIG_DIFICULDADE[dificuldade]["tempo_power"]
            try:
                sounds.coin_pickup.play()
            except: pass

    # Lógica de Som: Vitória
    if not cristais and not super_cristais and modo_de_jogo == "JOGANDO":
        modo_de_jogo = "VITORIA"
        try: sounds.powerup.play()
        except: pass

    vel_ini = CONFIG_DIFICULDADE[dificuldade]["vel_inimigo"]
    vel_atual = vel_ini // 2 if tempo_super > 0 else vel_ini
    
    for inimigo in inimigos:
        inimigo.atualizar_movimento(vel_atual)

        if jogador_rect.colliderect(inimigo.rect):
            if tempo_super > 0:
                pontuacao += 200
                inimigo.resetar_posicao()
                # Som ao devorar o fantasma
                try: sounds.coin_pickup.play()
                except: pass
            else:
                vidas -= 1
                jogador_rect.x = 45; jogador_rect.y = 45
                direcao_x = 0; direcao_y = 0
                # Som ao tomar dano
                try: sounds.dano.play()
                except: pass
                
                if vidas <= 0:
                    modo_de_jogo = "FIM"
                    # Som de Game Over
                    try: sounds.gameover.play()
                    except: pass

def on_key_down(key):
    global modo_de_jogo, dificuldade, prox_dir_x, prox_dir_y
    
    if modo_de_jogo == "MENU" and key == keys.SPACE:
        modo_de_jogo = "DIFICULDADE"
        
    elif modo_de_jogo == "DIFICULDADE":
        if key == keys.K_1 or key == keys.NUMPAD1:
            dificuldade = "NORMAL"; inicializar_fase(); modo_de_jogo = "JOGANDO"
        elif key == keys.K_2 or key == keys.NUMPAD2:
            dificuldade = "DIFICIL"; inicializar_fase(); modo_de_jogo = "JOGANDO"
        elif key == keys.K_3 or key == keys.NUMPAD3:
            dificuldade = "INSANO"; inicializar_fase(); modo_de_jogo = "JOGANDO"
            
    elif (modo_de_jogo == "FIM" or modo_de_jogo == "VITORIA") and key == keys.SPACE:
        modo_de_jogo = "MENU"
        
    elif modo_de_jogo == "JOGANDO":
        if key == keys.LEFT:
            prox_dir_x = -1; prox_dir_y = 0
        elif key == keys.RIGHT:
            prox_dir_x = 1; prox_dir_y = 0
        elif key == keys.UP:
            prox_dir_x = 0; prox_dir_y = -1
        elif key == keys.DOWN:
            prox_dir_x = 0; prox_dir_y = 1

pgzrun.go()