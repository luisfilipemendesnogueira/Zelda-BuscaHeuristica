import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from itertools import permutations
import os
from zelda_pathfinder import ler_mapa, heuristica, vizinhos, a_star

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

        # Frame de informações
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # Label de informações
        self.info_label = ttk.Label(info_frame, text="Clique em 'Carregar Mapas' para começar")
        self.info_label.pack(side=tk.LEFT)

        # Label de custos
        self.custos_label = ttk.Label(info_frame, text="")
        self.custos_label.pack(side=tk.RIGHT)

        # Notebook (abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Canvas de cada aba
        self.canvas_tabs = []
        self.frames_tabs = []
        self.cell_size = 15

        tab_names = ["Mapa Principal", "Masmorra 1", "Masmorra 2", "Masmorra 3"]
        for i in range(4):
            frame = ttk.Frame(self.notebook)
            canvas = tk.Canvas(frame, bg='white')
            canvas.pack(fill=tk.BOTH, expand=True)
            self.notebook.add(frame, text=tab_names[i])
            self.canvas_tabs.append(canvas)
            self.frames_tabs.append(frame)

        # Evento para desenhar o mapa/masmorra ao trocar de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.aba_trocada)

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

    def aba_trocada(self, event=None):
        aba = self.notebook.index(self.notebook.select())
        if aba == 0:
            self.desenhar_mapa()
        elif aba == 1 and self.masmorra1:
            self.desenhar_masmorra(self.masmorra1, 0)
        elif aba == 2 and self.masmorra2:
            self.desenhar_masmorra(self.masmorra2, 1)
        elif aba == 3 and self.masmorra3:
            self.desenhar_masmorra(self.masmorra3, 2)
        
    def carregar_mapas(self):
        """Carrega os mapas a partir dos arquivos"""
        try:
            # Verifica se os arquivos existem
            arquivos_necessarios = ['Mapa.txt', 'Masmorra 1.txt', 'Masmorra 2.txt', 'Masmorra 3.txt']
            for arquivo in arquivos_necessarios:
                if not os.path.exists(arquivo):
                    raise FileNotFoundError(f"Arquivo {arquivo} não encontrado")
            
            # Carrega mapas
            self.mapa = ler_mapa('Mapa.txt', 42)
            self.masmorra1 = ler_mapa('Masmorra 1.txt', 28)
            self.masmorra2 = ler_mapa('Masmorra 2.txt', 28)
            self.masmorra3 = ler_mapa('Masmorra 3.txt', 28)
            
            if None in [self.mapa, self.masmorra1, self.masmorra2, self.masmorra3]:
                raise ValueError("Falha ao carregar um ou mais mapas")
            
            messagebox.showinfo("Sucesso", "Mapas carregados com sucesso!")
            self.info_label.config(text="Mapas carregados. Clique em 'Calcular Melhor Caminho'")
            self.desenhar_mapa()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar mapas: {e}")
            self.info_label.config(text="Erro ao carregar mapas")
    
    def desenhar_mapa(self):
        """Desenha o mapa principal na aba 0"""
        if not self.mapa:
            return
        canvas = self.canvas_tabs[0]
        canvas.delete("all")
        for i, linha in enumerate(self.mapa):
            for j, cel in enumerate(linha):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                cor = self.cores.get(cel, '#FFFFFF')
                canvas.create_rectangle(x1, y1, x2, y2,
                                       fill=cor, outline='gray', width=0.5)
                if cel == 'LW':
                    img_x = x1 + self.cell_size//1.8
                    img_y = y2 - 5
                    canvas.create_image(img_x, img_y, image=self.lost_woods_img, anchor=tk.CENTER)
                elif cel == 'MA':
                    img_x = x1 + self.cell_size//2
                    img_y = y2 - 5
                    canvas.create_image(img_x, img_y, image=self.ma_img, anchor=tk.CENTER)
                elif cel == 'MS':
                    img_x = x1 + self.cell_size//2
                    img_y = y2 - 5
                    canvas.create_image(img_x, img_y, image=self.ms_img, anchor=tk.CENTER)
                elif cel == 'L':
                    img_x = x1 + self.cell_size//2
                    img_y = y2 - 5
                    canvas.create_image(img_x, img_y, image=self.link_img, anchor=tk.CENTER)
        canvas.configure(scrollregion=canvas.bbox("all"))

    def desenhar_masmorra(self, masmorra, idx):
        """Desenha uma masmorra na aba idx+1"""
        canvas = self.canvas_tabs[idx+1]
        canvas.delete("all")
        for i, linha in enumerate(masmorra):
            for j, cel in enumerate(linha):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                cor = self.cores.get(cel, '#FFFFFF')
                canvas.create_rectangle(x1, y1, x2, y2,
                                       fill=cor, outline='gray', width=0.5)
                if cel in ['P', 'E', 'CC']:
                    canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                      text=cel, font=('Arial', 6), fill='black')
        canvas.configure(scrollregion=canvas.bbox("all"))

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
                    caminho, custo = a_star(self.mapa, pos, entradas[idx], self.terrain_costs)
                    if caminho is None:
                        total_custo = float('inf')
                        break
                    
                    total_custo += custo
                    caminho_completo.extend(caminho[1:])  # Evita duplicar posição atual
                    
                    # Dentro da masmorra: entrada -> pingente
                    masmorra_atual = [self.masmorra1, self.masmorra2, self.masmorra3][idx]
                    caminho_masmorra, custo_masmorra = a_star(
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
                    caminho_volta, custo_volta = a_star(
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
                caminho, custo = a_star(self.mapa, pos, lost_woods, self.terrain_costs)
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
        """Desenha o caminho na aba atualmente aberta"""
        aba = self.notebook.index(self.notebook.select())
        if aba == 0:
            if not self.melhor_caminho:
                return
            self.desenhar_mapa()
            canvas = self.canvas_tabs[0]
            for i, j in self.melhor_caminho:
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                canvas.create_rectangle(x1, y1, x2, y2,
                                       fill=self.cores['L'], outline='red', width=2)
            # Marca posição inicial (Link)
            if self.melhor_caminho:
                start_i, start_j = self.melhor_caminho[0]
                x = start_j * self.cell_size + self.cell_size // 2
                y = start_i * self.cell_size + self.cell_size // 2
                canvas.create_oval(x-5, y-5, x+5, y+5, fill='green', outline='darkgreen', width=2)
                canvas.create_text(x, y, text="L", font=('Arial', 8, 'bold'), fill='white')
        elif aba in [1,2,3]:
            idx = aba-1
            caminho = self.caminhos_masmorras[idx] if self.caminhos_masmorras[idx] else None
            masmorra = [self.masmorra1, self.masmorra2, self.masmorra3][idx]
            if not caminho or not masmorra:
                return
            self.desenhar_masmorra(masmorra, idx)
            canvas = self.canvas_tabs[aba]
            for i, j in caminho:
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                canvas.create_rectangle(x1, y1, x2, y2,
                                       fill=self.cores['L'], outline='red', width=2)
            # Marca posição inicial
            if caminho:
                start_i, start_j = caminho[0]
                x = start_j * self.cell_size + self.cell_size // 2
                y = start_i * self.cell_size + self.cell_size // 2
                canvas.create_oval(x-5, y-5, x+5, y+5, fill='green', outline='darkgreen', width=2)
                canvas.create_text(x, y, text="L", font=('Arial', 8, 'bold'), fill='white')

    def animar_caminho(self):
        """Inicia a animação do caminho na aba ativa"""
        aba = self.notebook.index(self.notebook.select())
        if aba == 0:
            if not self.melhor_caminho:
                messagebox.showwarning("Aviso", "Calcule o caminho primeiro!")
                return
        elif aba in [1,2,3]:
            idx = aba-1
            if not self.caminhos_masmorras[idx]:
                messagebox.showwarning("Aviso", "Calcule o caminho da masmorra primeiro!")
                return
        if self.animando:
            return
        self.animando = True
        thread = threading.Thread(target=lambda: self._executar_animacao_aba(aba))
        thread.daemon = True
        thread.start()

    def _executar_animacao_aba(self, aba):
        try:
            if aba == 0:
                self.root.after(0, self.desenhar_mapa)
                canvas = self.canvas_tabs[0]
                for i, (pos_i, pos_j) in enumerate(self.melhor_caminho):
                    if not self.animando:
                        break
                    self.root.after(0, self._atualizar_posicao_link, pos_i, pos_j, i)
                    time.sleep(0.1)
                if self.animando:
                    self.root.after(0, lambda: self.info_label.config(text="Animação concluída no mapa principal!"))
            elif aba in [1,2,3]:
                idx = aba-1
                masmorra = [self.masmorra1, self.masmorra2, self.masmorra3][idx]
                self.root.after(0, lambda: self.desenhar_masmorra(masmorra, idx))
                canvas = self.canvas_tabs[aba]
                caminho = self.caminhos_masmorras[idx]
                for step, (pos_i, pos_j) in enumerate(caminho):
                    if not self.animando:
                        break
                    self.root.after(0, self._atualizar_posicao_masmorra, idx, pos_i, pos_j, step)
                    time.sleep(0.05)
                if self.animando:
                    self.root.after(0, lambda: self.info_label.config(text=f"Animação concluída na Masmorra {idx+1}!"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro na animação: {e}"))
        finally:
            self.animando = False

    def _atualizar_posicao_link(self, pos_i, pos_j, step):
        """Atualiza a posição de Link no canvas do mapa principal"""
        canvas = self.canvas_tabs[0]
        canvas.delete("link")
        x = pos_j * self.cell_size + self.cell_size // 2
        y = pos_i * self.cell_size + self.cell_size // 2
        canvas.create_oval(x-6, y-6, x+6, y+6,
                           fill='lime', outline='darkgreen', width=2, tags="link")
        canvas.create_text(x, y, text="L", font=('Arial', 8, 'bold'),
                           fill='darkgreen', tags="link")
        total_steps = len(self.melhor_caminho)
        progresso = (step + 1) / total_steps * 100
        self.info_label.config(text=f"Animando... {step+1}/{total_steps} ({progresso:.1f}%)")
        canvas.see(canvas.create_rectangle(x-50, y-50, x+50, y+50))

    def _atualizar_posicao_masmorra(self, idx, pos_i, pos_j, step):
        """Atualiza a posição de Link na aba da masmorra"""
        canvas = self.canvas_tabs[idx+1]
        canvas.delete(f"link_masmorra_{idx}")
        x = pos_j * self.cell_size + self.cell_size // 2
        y = pos_i * self.cell_size + self.cell_size // 2
        canvas.create_oval(x-5, y-5, x+5, y+5,
                           fill='blue', outline='darkblue', width=2,
                           tags=f"link_masmorra_{idx}")
        canvas.create_text(x, y, text="L", font=('Arial', 8, 'bold'),
                           fill='white', tags=f"link_masmorra_{idx}")
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