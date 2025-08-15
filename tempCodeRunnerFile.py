import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from itertools import permutations
import os

# Importa as funções e constantes do seu outro arquivo
from zelda_pathfinder import ler_mapa, a_star, TERRAIN_COSTS, MASMORRA_COST

class ZeldaPathFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Zelda - Caminho Otimizado de Link")
        self.root.geometry("1200x750")
        
        try:
            self.lost_woods_img = self.resize_image(tk.PhotoImage(file='LW.png'), 12)
            self.ma_img = self.resize_image(tk.PhotoImage(file='MA.png'), 10)
            self.ms_img = self.resize_image(tk.PhotoImage(file='MS.png'), 12)
            self.link_img = self.resize_image(tk.PhotoImage(file='Link.png'), 15)
        except tk.TclError:
            messagebox.showwarning("Imagens não encontradas", "Algumas imagens (.png) não foram encontradas.")
            self.lost_woods_img = self.ma_img = self.ms_img = self.link_img = None
        
        self.cores = {
            'G': '#92d050', 'S': '#c4bc96', 'F': '#00b050', 'M': '#948a54', 'A': '#548dd4',
            'LW': '#92d050', 'MA': '#c4bc96', 'L': '#92d050', 'MS': '#92d050',
            'X': '#3e2f0f', 'CC': '#D3D3D3', 'P': '#FF1493', 'E': '#00FF00',
        }
        
        # As constantes agora são importadas
        self.terrain_costs = TERRAIN_COSTS
        self.masmorra_cost = MASMORRA_COST
        
        self.setup_ui()
        self.carregar_mapas()
        
    def resize_image(self, img, target_size):
        scale = max(img.width() / target_size, img.height() / target_size)
        return img.subsample(int(scale) if scale > 1 else 1)
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(control_frame, text="Carregar Mapas", command=self.carregar_mapas).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Calcular Melhor Caminho", command=self.calcular_caminho).pack(side=tk.LEFT, padx=(0, 5))
        self.animar_btn = ttk.Button(control_frame, text="Animar Caminho", command=self.animar_caminho, state=tk.DISABLED)
        self.animar_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.parar_btn = ttk.Button(control_frame, text="Parar Animação", command=self.parar_animacao, state=tk.DISABLED)
        self.parar_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.info_label = ttk.Label(main_frame, text="...", font=("Segoe UI", 10))
        self.info_label.pack(fill=tk.X)
        self.custos_label = ttk.Label(main_frame, text="", font=("Segoe UI", 9))
        self.custos_label.pack(fill=tk.X)
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.cell_size = 15
        self.mapa = self.masmorra1 = self.masmorra2 = self.masmorra3 = None
        self.melhor_percurso_completo = None
        self.animando = False
        
    def carregar_mapas(self):
        try:
            # A função ler_mapa importada agora levanta exceções que podemos capturar
            self.mapa = ler_mapa('Mapa.txt', 42)
            self.masmorra1 = ler_mapa('Masmorra 1.txt', 28)
            self.masmorra2 = ler_mapa('Masmorra 2.txt', 28)
            self.masmorra3 = ler_mapa('Masmorra 3.txt', 28)
            self.info_label.config(text="Mapas carregados. Clique em 'Calcular Melhor Caminho'.")
            self.desenhar_mapa()
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Erro ao Carregar Mapas", str(e))
            self.info_label.config(text=f"Erro ao carregar mapas.")

    def desenhar_mapa(self, mapa_data=None, offset_x=0, offset_y=0, tags="mapa_principal"):
        if mapa_data is None:
            mapa_data = self.mapa
            if not mapa_data: return
            self.canvas.delete("all")
        
        for i, row in enumerate(mapa_data):
            for j, cel in enumerate(row):
                x1, y1 = j * self.cell_size + offset_x, i * self.cell_size + offset_y
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                cor = self.cores.get(cel, '#FFFFFF')
                rect_tags = (tags, f"{tags}-{i}-{j}")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=cor, outline='#E0E0E0', width=1, tags=rect_tags)
                img_to_draw = None
                if cel == 'LW' and self.lost_woods_img: img_to_draw = self.lost_woods_img
                elif cel == 'MA' and self.ma_img: img_to_draw = self.ma_img
                elif cel == 'MS' and self.ms_img: img_to_draw = self.ms_img
                elif cel == 'L' and self.link_img: img_to_draw = self.link_img
                if img_to_draw:
                    self.canvas.create_image(x1 + self.cell_size/2, y1 + self.cell_size/2, image=img_to_draw, tags=rect_tags)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def calcular_caminho(self):
        if not all([self.mapa, self.masmorra1, self.masmorra2, self.masmorra3]):
            messagebox.showerror("Erro", "Mapas não foram carregados corretamente.")
            return
        self.info_label.config(text="Calculando melhor caminho...")
        self.root.update()
        calc_thread = threading.Thread(target=self._worker_calcular_caminho)
        calc_thread.daemon = True
        calc_thread.start()

    def _worker_calcular_caminho(self):
        try:
            start = next((i, j) for i, r in enumerate(self.mapa) for j, c in enumerate(r) if c == 'L')
            lost_woods = next((i, j) for i, r in enumerate(self.mapa) for j, c in enumerate(r) if c == 'LW')
            entradas = sorted([(i, j) for i, r in enumerate(self.mapa) for j, c in enumerate(r) if c == 'MA'])
            pingentes = [next((i, j) for i, r in enumerate(m) for j, c in enumerate(r) if c == 'P') for m in [self.masmorra1, self.masmorra2, self.masmorra3]]
            
            menor_custo = float('inf')
            melhor_percurso_final = None

            for ordem in permutations([0, 1, 2]):
                pos, total_custo_atual, percurso_completo_atual = start, 0, []
                mapas = [self.masmorra1, self.masmorra2, self.masmorra3]
                caminho_inviavel = False

                for i in range(3):
                    masmorra_idx = ordem[i]
                    caminho_mapa, custo_mapa = a_star(self.mapa, pos, entradas[masmorra_idx], self.terrain_costs)
                    if caminho_mapa is None: caminho_inviavel = True; break
                    total_custo_atual += custo_mapa
                    percurso_completo_atual.append({'type': 'main_map', 'path': caminho_mapa if i == 0 else caminho_mapa[1:]})

                    masmorra_atual = mapas[masmorra_idx]
                    entrada_m = next((i, j) for i, r in enumerate(masmorra_atual) for j, c in enumerate(r) if c == 'E')
                    custos_m = {'CC': self.masmorra_cost, 'P': self.masmorra_cost, 'E': self.masmorra_cost}
                    walkable_m = {'CC', 'P', 'E'}
                    
                    caminho_ida, custo_ida = a_star(masmorra_atual, entrada_m, pingentes[masmorra_idx], custos_m, walkable_m)
                    if caminho_ida is None: caminho_inviavel = True; break
                    
                    caminho_volta, custo_volta = caminho_ida[::-1], custo_ida
                    
                    total_custo_atual += custo_ida + custo_volta
                    percurso_completo_atual.append({
                        'type': 'dungeon', 'id': masmorra_idx + 1, 'mapa': masmorra_atual,
                        'custo_total': custo_ida + custo_volta,
                        'path': caminho_ida + caminho_volta[1:]
                    })
                    pos = entradas[masmorra_idx]
                
                if caminho_inviavel: continue
                caminho_final, custo_final = a_star(self.mapa, pos, lost_woods, self.terrain_costs)
                if caminho_final is None: continue
                total_custo_atual += custo_final
                percurso_completo_atual.append({'type': 'main_map', 'path': caminho_final[1:]})

                if total_custo_atual < menor_custo:
                    menor_custo = total_custo_atual
                    melhor_percurso_final = {
                        'custo_total': menor_custo,
                        'ordem': [o + 1 for o in ordem],
                        'segmentos': percurso_completo_atual
                    }
            
            if melhor_percurso_final is None: raise ValueError("Nenhum caminho válido encontrado.")
            self.melhor_percurso_completo = melhor_percurso_final
            self.root.after(0, self.update_ui_apos_calculo)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro de Cálculo", f"{e}"))

    def update_ui_apos_calculo(self):
        data = self.melhor_percurso_completo
        ordem_str = ' -> '.join(map(str, data['ordem']))
        self.info_label.config(text=f"Cálculo concluído! Ordem: {ordem_str}. Custo total: {data['custo_total']}")
        
        dungeons = [s for s in data['segmentos'] if s['type'] == 'dungeon']
        custos_str = " | ".join([f"Masmorra {d['id']}: {d['custo_total']}" for d in dungeons])
        self.custos_label.config(text=f"Custos: {custos_str}")
        
        self.desenhar_mapa()
        self.animar_btn.config(state=tk.NORMAL)

    def animar_caminho(self):
        if not self.melhor_percurso_completo: return
        if self.animando: return
        self.animando = True
        self.animar_btn.config(state=tk.DISABLED)
        self.parar_btn.config(state=tk.NORMAL)
        thread = threading.Thread(target=self._executar_animacao)
        thread.daemon = True
        thread.start()
        
    def _executar_animacao(self):
        try:
            self.root.after(0, self.desenhar_mapa)
            time.sleep(0.2)

            for segment in self.melhor_percurso_completo['segmentos']:
                if not self.animando: raise InterruptedError()

                if segment['type'] == 'main_map':
                    self.info_label.config(text="Percorrendo Hyrule...")
                    for pos in segment['path']:
                        if not self.animando: raise InterruptedError()
                        self.root.after(0, self._atualizar_posicao_link, pos, "mapa_principal")
                        time.sleep(0.04)

                elif segment['type'] == 'dungeon':
                    masmorra_info = segment
                    self.info_label.config(text=f"Entrando na Masmorra {masmorra_info['id']}...")
                    time.sleep(0.5)

                    offset_x = (42 + 3) * self.cell_size
                    offset_y = 5 * self.cell_size
                    tag_masmorra = f"dungeon_display_{masmorra_info['id']}"

                    self.root.after(0, self.desenhar_mapa, masmorra_info['mapa'], offset_x, offset_y, tag_masmorra)
                    self.root.after(0, self._desenhar_titulo_masmorra, masmorra_info, offset_x, offset_y, tag_masmorra)
                    time.sleep(0.2)

                    for pos in masmorra_info['path']:
                        if not self.animando: raise InterruptedError()
                        self.root.after(0, self._atualizar_posicao_link, pos, tag_masmorra, offset_x, offset_y)
                        time.sleep(0.04)
                    
                    self.info_label.config(text=f"Saindo da Masmorra {masmorra_info['id']}...")
                    time.sleep(0.5)
                    self.root.after(0, lambda: self.canvas.delete(tag_masmorra))

            self.root.after(0, lambda: self.info_label.config(text="Animação concluída!"))
        except InterruptedError:
            self.root.after(0, lambda: self.info_label.config(text="Animação interrompida."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro de Animação", f"{e}"))
        finally:
            self.animando = False
            self.root.after(0, lambda: self.animar_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.parar_btn.config(state=tk.DISABLED))
    
    def _desenhar_titulo_masmorra(self, masmorra_info, offset_x, offset_y, tags):
        self.canvas.create_text(
            offset_x + 14 * self.cell_size, offset_y - 15,
            text=f"Masmorra {masmorra_info['id']} (Custo: {masmorra_info['custo_total']})",
            font=('Segoe UI', 10, 'bold'), fill='black', anchor=tk.CENTER, tags=tags
        )

    def _atualizar_posicao_link(self, pos, tag, offset_x=0, offset_y=0):
        self.canvas.delete("link_icon")
        i, j = pos
        x = j * self.cell_size + self.cell_size / 2 + offset_x
        y = i * self.cell_size + self.cell_size / 2 + offset_y
        
        self.canvas.itemconfigure(f"{tag}-{i}-{j}", fill="yellow")
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='#228B22', outline='darkgreen', width=1.5, tags="link_icon")
        
        if self.animando:
            # Tenta centralizar a visão no Link
            try:
                bbox = self.canvas.bbox("all")
                if bbox:
                    total_width = bbox[2] - bbox[0]
                    total_height = bbox[3] - bbox[1]
                    if total_width > 0 and total_height > 0:
                        self.canvas.xview_moveto(max(0, (x - self.canvas.winfo_width()/2) / total_width))
                        self.canvas.yview_moveto(max(0, (y - self.canvas.winfo_height()/2) / total_height))
            except (tk.TclError, ZeroDivisionError):
                # Ignora erros que podem ocorrer durante o setup inicial do canvas
                pass

    def parar_animacao(self):
        self.animando = False

if __name__ == "__main__":
    root = tk.Tk()
    app = ZeldaPathFinder(root)
    root.mainloop()