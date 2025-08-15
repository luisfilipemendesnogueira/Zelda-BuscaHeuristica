    import tkinter as tk
    from tkinter import ttk, messagebox
    import heapq
    import threading
    import time
    from itertools import permutations
    import os

    class ZeldaPathFinder:
        def __init__(self, root):
            self.root = root
            self.root.title("Zelda - Caminho Otimizado de Link")
            self.root.geometry("1200x800")
            
            # Imagens dos personagens
            self.lost_woods_img = self.resize_image(tk.PhotoImage(file='LW.png'), 12)
            self.ma_img = self.resize_image(tk.PhotoImage(file='MA.png'), 10)
            self.ms_img = self.resize_image(tk.PhotoImage(file='MS.png'), 12)
            self.link_img = self.resize_image(tk.PhotoImage(file='Link.png'), 25)
            
            # Cores dos terrenos
            self.cores = {
                'G': '#92d050',    # Verde claro - Grama
                'S': '#c4bc96',    # Marrom claro - Areia
                'F': '#00b050',    # Verde Escuro - Floresta
                'M': '#948a54',    # Marrom - Montanha
                'A': '#548dd4',    # Azul - Água
                'LW': '#92d050',   # Verde claro - Lost Woods
                'MA': '#c4bc96',   # Tomato - Entrada de Masmorra
                'L': '#92d050',    # Verde claro - Link
                'MS': '#92d050',   # Verde claro - Master Sword
                'X': '#3e2f0f',    # Marrom Escuro - Parede
                'CC': '#D3D3D3',   # Light Gray - Caminho Claro
                'P': '#FF1493',    # Deep Pink - Pingente
                'E': '#00FF00',    # Lime - Entrada da masmorra
            }
            
            # Custos dos terrenos
            self.terrain_costs = {
                'G': 10, 'S': 20, 'F': 100, 'M': 150, 'A': 180, 'LW': 10, 'MA': 20
            }
            self.masmorra_cost = 10
            
            self.setup_ui()
            self.carregar_mapas()
            
        def resize_image(self, img, target_size):
            """Redimensiona imagem mantendo aspect ratio para o tamanho máximo especificado"""
            width = img.width()
            height = img.height()
            
            # Calcula o fator de escala
            scale = max(width/target_size, height/target_size)
            
            # Aplica o subsample
            return img.subsample(int(scale))    
            
        def setup_ui(self):
            # Frame principal
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Frame de controles
            control_frame = ttk.Frame(main_frame)
            control_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Botões
            ttk.Button(control_frame, text="Carregar Mapas", 
                    command=self.carregar_mapas).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(control_frame, text="Calcular Melhor Caminho", 
                    command=self.calcular_caminho).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(control_frame, text="Animar Caminho", 
                    command=self.animar_caminho).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(control_frame, text="Parar Animação", 
                    command=self.parar_animacao).pack(side=tk.LEFT, padx=(0, 10))
            
            # Frame de informações
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Label de informações
            self.info_label = ttk.Label(info_frame, text="Clique em 'Carregar Mapas' para começar")
            self.info_label.pack(side=tk.LEFT)
            
            # Label de custos
            self.custos_label = ttk.Label(info_frame, text="")
            self.custos_label.pack(side=tk.RIGHT)
            
            # Frame do canvas
            canvas_frame = ttk.Frame(main_frame)
            canvas_frame.pack(fill=tk.BOTH, expand=True)
            
            # Canvas com scrollbars
            self.canvas = tk.Canvas(canvas_frame, bg='white')
            h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
            v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            
            self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
            
            h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
            v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Tamanho das células
            self.cell_size = 15
            
            # Variáveis de controle
            self.mapa = None
            self.masmorra1 = None
            self.masmorra2 = None
            self.masmorra3 = None
            self.melhor_caminho = None
            self.melhor_ordem = None
            self.menor_custo = 0
            self.custos_masmorras = [0, 0, 0]
            self.caminhos_masmorras = [[], [], []]
            self.animando = False
            
        def ler_mapa_arquivo(self, caminho_arquivo, tamanho_esperado):
            """Lê um mapa de um arquivo e retorna como matriz"""
            try:
                with open(caminho_arquivo, 'r') as f:
                    linhas = [linha.strip() for linha in f if linha.strip()]
                    
                mapa = []
                for linha in linhas:
                    celulas = [c.strip() for c in linha.split(',')]
                    mapa.append(celulas)
                
                # Verifica se o tamanho está correto
                if len(mapa) != tamanho_esperado or any(len(linha) != tamanho_esperado for linha in mapa):
                    raise ValueError(f"Tamanho do mapa incorreto. Esperado: {tamanho_esperado}x{tamanho_esperado}")
                
                return mapa
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler arquivo {caminho_arquivo}: {str(e)}")
                return None
            
        def carregar_mapas(self):
            """Carrega os mapas a partir dos arquivos"""
            try:
                # Verifica se os arquivos existem
                arquivos_necessarios = ['Mapa.txt', 'Masmorra 1.txt', 'Masmorra 2.txt', 'Masmorra 3.txt']
                for arquivo in arquivos_necessarios:
                    if not os.path.exists(arquivo):
                        raise FileNotFoundError(f"Arquivo {arquivo} não encontrado")
                
                # Carrega mapas
                self.mapa = self.ler_mapa_arquivo('Mapa.txt', 42)
                self.masmorra1 = self.ler_mapa_arquivo('Masmorra 1.txt', 28)
                self.masmorra2 = self.ler_mapa_arquivo('Masmorra 2.txt', 28)
                self.masmorra3 = self.ler_mapa_arquivo('Masmorra 3.txt', 28)
                
                if None in [self.mapa, self.masmorra1, self.masmorra2, self.masmorra3]:
                    raise ValueError("Falha ao carregar um ou mais mapas")
                
                messagebox.showinfo("Sucesso", "Mapas carregados com sucesso!")
                self.info_label.config(text="Mapas carregados. Clique em 'Calcular Melhor Caminho'")
                self.desenhar_mapa()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar mapas: {e}")
                self.info_label.config(text="Erro ao carregar mapas")
        
        def desenhar_mapa(self):
            """Desenha o mapa principal no canvas"""
            if not self.mapa:
                return
                
            self.canvas.delete("all")
            
            for i, linha in enumerate(self.mapa):
                for j, cel in enumerate(linha):
                    x1 = j * self.cell_size
                    y1 = i * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    
                    cor = self.cores.get(cel, '#FFFFFF')
                    
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                            fill=cor, outline='gray', width=0.5)
                    
                    # Adiciona texto para elementos especiais
                    if cel == 'LW':
                        img_x = x1 + self.cell_size//1.8
                        img_y = y2 - 5
                        self.canvas.create_image(img_x, img_y, image=self.lost_woods_img, anchor=tk.CENTER)
                        
                    elif cel == 'MA':
                        # Entrada de Masmorra
                        img_x = x1 + self.cell_size//2
                        img_y = y2 - 5
                        self.canvas.create_image(img_x, img_y, image=self.ma_img, anchor=tk.CENTER)
                        
                    elif cel == 'MS':
                        # Master Sword
                        img_x = x1 + self.cell_size//2
                        img_y = y2 - 5
                        self.canvas.create_image(img_x, img_y, image=self.ms_img, anchor=tk.CENTER)
                        
                    elif cel == 'L':
                        # Link
                        img_x = x1 + self.cell_size//2
                        img_y = y2 - 5
                        self.canvas.create_image(img_x, img_y, image=self.link_img, anchor=tk.CENTER)
            
            # Configura scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        def desenhar_masmorra(self, masmorra, offset_x=0, offset_y=0):
            """Desenha uma masmorra no canvas com offset"""
            for i, linha in enumerate(masmorra):
                for j, cel in enumerate(linha):
                    x1 = j * self.cell_size + offset_x
                    y1 = i * self.cell_size + offset_y
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    
                    cor = self.cores.get(cel, '#FFFFFF')
                    
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                            fill=cor, outline='gray', width=0.5)
                    
                    # Adiciona texto para elementos especiais
                    if cel in ['P', 'E', 'CC']:
                        self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                            text=cel, font=('Arial', 6), fill='black')
        
        def heuristica(self, a, b):
            """Distância de Manhattan"""
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def vizinhos(self, pos, size):
            """Retorna vizinhos válidos"""
            x, y = pos
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < size and 0 <= ny < size:
                    yield (nx, ny)
        
        def a_star(self, mapa, start, goal, terrain_costs, walkable=None):
            """Busca A*"""
            size = len(mapa)
            open_set = []
            heapq.heappush(open_set, (0, start))
            came_from = {}
            g_score = {start: 0}
            f_score = {start: self.heuristica(start, goal)}

            while open_set:
                _, current = heapq.heappop(open_set)
                if current == goal:
                    # Reconstrói caminho
                    caminho = [current]
                    while current in came_from:
                        current = came_from[current]
                        caminho.append(current)
                    caminho.reverse()
                    return caminho, g_score[goal]

                for neighbor in self.vizinhos(current, size):
                    x, y = neighbor
                    cel = mapa[x][y]
                    if walkable and cel not in walkable:
                        continue
                    cost = terrain_costs.get(cel, 9999)
                    tentative_g = g_score[current] + cost
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self.heuristica(neighbor, goal)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
            return None, float('inf')
        
        def encontrar_posicao(self, mapa, simbolo):
            """Encontra a posição de um símbolo no mapa"""
            for i, linha in enumerate(mapa):
                for j, cel in enumerate(linha):
                    if cel == simbolo:
                        return (i, j)
            return None
        
        def calcular_caminho(self):
            """Calcula o melhor caminho"""
            if not self.mapa or not self.masmorra1 or not self.masmorra2 or not self.masmorra3:
                messagebox.showerror("Erro", "Carregue os mapas primeiro!")
                return
                
            self.info_label.config(text="Calculando melhor caminho...")
            self.root.update()
            
            try:
                # Posições fixas
                start = (25, 28)  # Casa do Link (posição inicial)
                lost_woods = self.encontrar_posicao(self.mapa, 'LW')
                
                # Encontra entradas das masmorras no mapa principal
                entradas = []
                for i in range(42):
                    for j in range(42):
                        if self.mapa[i][j] == 'MA':
                            entradas.append((i, j))
                
                if not lost_woods or len(entradas) != 3:
                    raise ValueError("Não foi possível encontrar todas as posições necessárias")
                
                # Encontra pingentes nas masmorras
                pingentes = [
                    self.encontrar_posicao(self.masmorra1, 'P'),
                    self.encontrar_posicao(self.masmorra2, 'P'),
                    self.encontrar_posicao(self.masmorra3, 'P')
                ]
                
                # Encontra entradas das masmorras (dentro dos mapas das masmorras)
                entradas_masmorras = [
                    self.encontrar_posicao(self.masmorra1, 'E'),
                    self.encontrar_posicao(self.masmorra2, 'E'),
                    self.encontrar_posicao(self.masmorra3, 'E')
                ]
                
                if None in pingentes or None in entradas_masmorras:
                    raise ValueError("Não foi possível encontrar pingentes ou entradas nas masmorras")
                
                # Testa todas as permutações de ordem das masmorras
                menor_custo = float('inf')
                melhor_ordem = None
                melhor_caminho_completo = []
                melhor_caminhos_masmorras = [[], [], []]
                melhor_custos_masmorras = [0, 0, 0]
                
                for ordem in permutations([0, 1, 2]):
                    pos = start
                    total_custo = 0
                    caminho_completo = [start]
                    custos_masmorras = [0, 0, 0]
                    caminhos_masmorras = [[], [], []]
                    
                    # Para cada masmorra na ordem atual
                    for idx in ordem:
                        # Caminho até entrada da masmorra no mapa principal
                        caminho, custo = self.a_star(self.mapa, pos, entradas[idx], self.terrain_costs)
                        if caminho is None:
                            total_custo = float('inf')
                            break
                        
                        total_custo += custo
                        caminho_completo.extend(caminho[1:])  # Evita duplicar posição atual
                        
                        # Dentro da masmorra: entrada -> pingente
                        masmorra_atual = [self.masmorra1, self.masmorra2, self.masmorra3][idx]
                        caminho_masmorra, custo_masmorra = self.a_star(
                            masmorra_atual,
                            entradas_masmorras[idx],
                            pingentes[idx],
                            {'CC': self.masmorra_cost, 'P': self.masmorra_cost, 'E': self.masmorra_cost},
                            walkable={'CC', 'P', 'E'}
                        )
                        
                        if caminho_masmorra is None:
                            total_custo = float('inf')
                            break
                        
                        total_custo += custo_masmorra
                        custos_masmorras[idx] += custo_masmorra
                        caminhos_masmorras[idx].extend(caminho_masmorra)
                        
                        # Volta para a entrada da masmorra
                        caminho_volta, custo_volta = self.a_star(
                            masmorra_atual,
                            pingentes[idx],
                            entradas_masmorras[idx],
                            {'CC': self.masmorra_cost, 'P': self.masmorra_cost, 'E': self.masmorra_cost},
                            walkable={'CC', 'P', 'E'}
                        )
                        
                        if caminho_volta is None:
                            total_custo = float('inf')
                            break
                        
                        total_custo += custo_volta
                        custos_masmorras[idx] += custo_volta
                        caminhos_masmorras[idx].extend(caminho_volta[1:])  # Evita duplicar posição
                        
                        pos = entradas[idx]
                    
                    if total_custo == float('inf'):
                        continue
                    
                    # Caminho final até Lost Woods
                    caminho, custo = self.a_star(self.mapa, pos, lost_woods, self.terrain_costs)
                    if caminho is None:
                        continue
                    
                    total_custo += custo
                    caminho_completo.extend(caminho[1:])
                    
                    # Verifica se é o melhor caminho
                    if total_custo < menor_custo:
                        menor_custo = total_custo
                        melhor_ordem = ordem
                        melhor_caminho_completo = caminho_completo.copy()
                        melhor_caminhos_masmorras = [caminhos_masmorras[i].copy() for i in range(3)]
                        melhor_custos_masmorras = custos_masmorras.copy()
                
                if melhor_ordem is None:
                    raise ValueError("Não foi possível encontrar um caminho válido")
                
                # Armazena resultados
                self.melhor_caminho = melhor_caminho_completo
                self.melhor_ordem = melhor_ordem
                self.menor_custo = menor_custo
                self.caminhos_masmorras = melhor_caminhos_masmorras
                self.custos_masmorras = melhor_custos_masmorras
                
                # Atualiza interface
                ordem_str = [str(x+1) for x in melhor_ordem]
                self.info_label.config(text=f"Melhor ordem: {', '.join(ordem_str)} | Custo total: {menor_custo}")
                
                # Atualiza label de custos
                custos_text = f"Custos: Masmorra 1: {self.custos_masmorras[0]} | " + \
                            f"Masmorra 2: {self.custos_masmorras[1]} | " + \
                            f"Masmorra 3: {self.custos_masmorras[2]}"
                self.custos_label.config(text=custos_text)
                
                # Desenha o caminho no mapa
                self.desenhar_caminho()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro no cálculo: {e}")
                self.info_label.config(text="Erro no cálculo do caminho")
        
        def desenhar_caminho(self):
            """Desenha o caminho no mapa"""
            if not self.melhor_caminho:
                return
            
            # Redesenha o mapa
            self.desenhar_mapa()
            
            # Desenha o caminho principal
            caminho_set = set(self.melhor_caminho)
            for i, j in self.melhor_caminho:
                if 0 <= i < 42 and 0 <= j < 42:  # Apenas no mapa principal
                    x1 = j * self.cell_size
                    y1 = i * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    
                    # Marca o caminho com uma cor especial
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                            fill=self.cores['L'], outline='red', width=2)
            
            # Marca posição inicial (Link)
            if self.melhor_caminho:
                start_i, start_j = self.melhor_caminho[0]
                x = start_j * self.cell_size + self.cell_size // 2
                y = start_i * self.cell_size + self.cell_size // 2
                self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='green', outline='darkgreen', width=2)
                self.canvas.create_text(x, y, text="L", font=('Arial', 8, 'bold'), fill='white')
        
        def animar_caminho(self):
            """Inicia a animação do caminho"""
            if not self.melhor_caminho:
                messagebox.showwarning("Aviso", "Calcule o caminho primeiro!")
                return
            
            if self.animando:
                return
            
            self.animando = True
            
            # Executa animação em thread separada
            thread = threading.Thread(target=self._executar_animacao)
            thread.daemon = True
            thread.start()
        
        def _executar_animacao(self):
            """Executa a animação do movimento de Link"""
            try:
                # Redesenha o mapa base
                self.root.after(0, self.desenhar_mapa)
                
                # Desenha caminho completo em cinza claro
                self.root.after(100, self._desenhar_caminho_completo)
                
                # Anima Link movendo-se pelo caminho principal
                for i, (pos_i, pos_j) in enumerate(self.melhor_caminho):
                    if not self.animando:
                        break
                        
                    if 0 <= pos_i < 42 and 0 <= pos_j < 42:
                        # Atualiza posição de Link
                        self.root.after(0, self._atualizar_posicao_link, pos_i, pos_j, i, False)
                        
                    time.sleep(0.1)  # Velocidade da animação
                
                # Se a animação foi interrompida, sair
                if not self.animando:
                    return
                
                # Anima as masmorras na ordem correta
                for idx in self.melhor_ordem:
                    # Desenha a masmorra
                    offset_x = 45 * self.cell_size  # Posição à direita do mapa principal
                    offset_y = idx * 30 * self.cell_size  # Espaço vertical entre masmorras
                    
                    self.root.after(0, self._desenhar_masmorra_completa, idx, offset_x, offset_y)
                    
                    # Anima o caminho na masmorra
                    for step, (pos_i, pos_j) in enumerate(self.caminhos_masmorras[idx]):
                        if not self.animando:
                            break
                            
                        self.root.after(0, self._atualizar_posicao_masmorra, idx, pos_i, pos_j, step, offset_x, offset_y)
                        time.sleep(0.05)  # Velocidade mais rápida para masmorras
                
                if self.animando:
                    self.root.after(0, lambda: self.info_label.config(
                        text=f"Animação concluída! Custo total: {self.menor_custo}\n" +
                        f"Masmorra 1: {self.custos_masmorras[0]} | " +
                        f"Masmorra 2: {self.custos_masmorras[1]} | " +
                        f"Masmorra 3: {self.custos_masmorras[2]}"
                    ))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro na animação: {e}"))
            finally:
                self.animando = False
        
        def _desenhar_masmorra_completa(self, idx, offset_x, offset_y):
            """Desenha uma masmorra completa no canvas"""
            masmorra = [self.masmorra1, self.masmorra2, self.masmorra3][idx]
            self.desenhar_masmorra(masmorra, offset_x, offset_y)
            
            # Adiciona título
            self.canvas.create_text(
                offset_x + 14 * self.cell_size, 
                offset_y - 10, 
                text=f"Masmorra {idx+1} (Custo: {self.custos_masmorras[idx]})", 
                font=('Arial', 10, 'bold'), 
                fill='black',
                anchor=tk.CENTER
            )
        
        def _desenhar_caminho_completo(self):
            """Desenha o caminho completo em cinza claro"""
            for i, j in self.melhor_caminho:
                if 0 <= i < 42 and 0 <= j < 42:
                    x1 = j * self.cell_size
                    y1 = i * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                            fill='lightgray', outline='gray', width=1,
                                            tags="caminho")
        
        def _atualizar_posicao_link(self, pos_i, pos_j, step, em_masmorra=False):
            """Atualiza a posição de Link no canvas"""
            # Remove Link anterior
            self.canvas.delete("link")
            
            # Desenha novo Link
            x = pos_j * self.cell_size + self.cell_size // 2
            y = pos_i * self.cell_size + self.cell_size // 2
            
            # Cor diferente para masmorra
            cor_fill = 'blue' if em_masmorra else 'lime'
            cor_outline = 'darkblue' if em_masmorra else 'darkgreen'
            
            # Link como círculo
            self.canvas.create_oval(x-6, y-6, x+6, y+6, 
                                fill=cor_fill, outline=cor_outline, width=2, tags="link")
            self.canvas.create_text(x, y, text="L", font=('Arial', 8, 'bold'), 
                                fill=cor_outline, tags="link")
            
            # Atualiza informação
            total_steps = len(self.melhor_caminho)
            progresso = (step + 1) / total_steps * 100
            self.info_label.config(text=f"Animando... {step+1}/{total_steps} ({progresso:.1f}%)")
            
            # Centraliza view no Link
            self.canvas.see(self.canvas.create_rectangle(x-50, y-50, x+50, y+50))
        
        def _atualizar_posicao_masmorra(self, idx, pos_i, pos_j, step, offset_x, offset_y):
            """Atualiza a posição de Link na masmorra"""
            # Remove Link anterior na masmorra
            self.canvas.delete(f"link_masmorra_{idx}")
            
            # Desenha novo Link na masmorra
            x = pos_j * self.cell_size + offset_x + self.cell_size // 2
            y = pos_i * self.cell_size + offset_y + self.cell_size // 2
            
            # Link como círculo azul na masmorra
            self.canvas.create_oval(x-5, y-5, x+5, y+5, 
                                fill='blue', outline='darkblue', width=2, 
                                tags=f"link_masmorra_{idx}")
            self.canvas.create_text(x, y, text="L", font=('Arial', 8, 'bold'), 
                                fill='white', tags=f"link_masmorra_{idx}")
            
            # Atualiza informação
            total_steps = len(self.caminhos_masmorras[idx])
            progresso = (step + 1) / total_steps * 100
            self.info_label.config(
                text=f"Explorando Masmorra {idx+1}... {step+1}/{total_steps} ({progresso:.1f}%)\n" +
                f"Custo: {self.custos_masmorras[idx]}"
            )
        
        def parar_animacao(self):
            """Para a animação"""
            self.animando = False
            self.info_label.config(text="Animação interrompida")


    # Classe principal para executar a aplicação
    class ZeldaApp:
        def __init__(self):
            self.root = tk.Tk()
            self.path_finder = ZeldaPathFinder(self.root)
        
        def run(self):
            """Executa a aplicação"""
            try:
                self.root.mainloop()
            except KeyboardInterrupt:
                print("\nAplicação encerrada pelo usuário")
            except Exception as e:
                messagebox.showerror("Erro Fatal", f"Erro inesperado: {e}")

    # Função principal
    def main():
        """Função principal da aplicação"""
        try:
            app = ZeldaApp()
            app.run()
        except Exception as e:
            print(f"Erro ao iniciar aplicação: {e}")

    if __name__ == "__main__":
        main()