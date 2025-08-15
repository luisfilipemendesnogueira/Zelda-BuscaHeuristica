import heapq
import os

# Custos dos terrenos
TERRAIN_COSTS = {
    'G': 10,   # Grama
    'S': 20,   # Areia
    'F': 100,  # Floresta
    'M': 150,  # Montanha
    'A': 180,  # Água
    'LW': 10,  # Lost Woods (entrada especial)
    'MA': 20,  # Entrada de masmorra
}

MASMORRA_COST = 10  # Caminho claro dentro das masmorras

def ler_mapa(path, size):
    """lê um mapa de arquivo texto e retorna uma matriz."""
    mapa = []
    with open(path, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                mapa.append([x.strip() for x in linha.split(',')])
    # Ajusta tamanho se necessário
    if len(mapa) != size:
        raise ValueError(f"Mapa {path} não tem tamanho {size}x{size}")
    return mapa

def print_mapa(mapa, caminho=None):
    caminho_set = set(caminho) if caminho else set()
    for i, linha in enumerate(mapa):
        out = ''
        for j, cel in enumerate(linha):
            if (i, j) in caminho_set:
                out += 'L '  # Link/caminho
            else:
                out += f'{cel} '
        print(out)
    print()

def heuristica(a, b):
    """Distância de Manhattan (sem diagonais)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def vizinhos(pos, size):
    """Retorna vizinhos válidos (vertical/horizontal)."""
    x, y = pos
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < size and 0 <= ny < size:
            yield (nx, ny)

def a_star(mapa, start, goal, terrain_costs, walkable=None):
    """Busca A* genérica."""
    size = len(mapa)
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristica(start, goal)}

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

        for neighbor in vizinhos(current, size):
            x, y = neighbor
            cel = mapa[x][y]
            if walkable and cel not in walkable:
                continue
            cost = terrain_costs.get(cel, 9999)
            tentative_g = g_score[current] + cost
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristica(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None, float('inf')  # Sem caminho

def main():
    # Lê mapas
    mapa = ler_mapa('Mapa.txt', 42)
    masmorra1 = ler_mapa('Masmorra 1.txt', 28)
    masmorra2 = ler_mapa('Masmorra 2.txt', 28)
    masmorra3 = ler_mapa('Masmorra 3.txt', 28)

    # Posições fixas
    start = (25, 28)  # Casa do Link
    lost_woods = (7, 6)  # Entrada de Lost Woods

    # Localiza entradas das masmorras e lost woods
    entradas = []
    for i in range(42):
        for j in range(42):
            if mapa[i][j] == 'MA':
                entradas.append((i, j))
            if mapa[i][j] == 'LW':
                lost_woods = (i, j)

    # Localiza pingentes nas masmorras
    def find_pingente(masmorra):
        for i in range(28):
            for j in range(28):
                if masmorra[i][j] == 'P':
                    return (i, j)
        return None
    pingentes = [find_pingente(masmorra1), find_pingente(masmorra2), find_pingente(masmorra3)]

    # Estratégia: múltiplas buscas (ordem dos pingentes pode ser alterada)
    from itertools import permutations
    menor_custo = float('inf')
    melhor_ordem = None
    melhor_caminho = None

    for ordem in permutations([0,1,2]):
        pos = start
        total_caminho = []
        total_custo = 0
        entradas_ordem = [entradas[i] for i in ordem]
        pingentes_ordem = [pingentes[i] for i in ordem]
        masmorras_ordem = [ [masmorra1, masmorra2, masmorra3][i] for i in ordem ]

        # Para cada masmorra
        for idx in range(3):
            # Caminho até entrada da masmorra
            caminho, custo = a_star(mapa, pos, entradas_ordem[idx], TERRAIN_COSTS)
            if caminho is None:
                break
            total_caminho += caminho[1:] if total_caminho else caminho
            total_custo += custo
            # Dentro da masmorra: entrada -> pingente
            entrada_masmorra = None
            for i in range(28):
                for j in range(28):
                    if masmorras_ordem[idx][i][j] == 'E':
                        entrada_masmorra = (i, j)
            caminho_m, custo_m = a_star(masmorras_ordem[idx], entrada_masmorra, pingentes_ordem[idx], {'CC': MASMORRA_COST, 'P': MASMORRA_COST, 'E': MASMORRA_COST}, walkable={'CC', 'P', 'E'})
            if caminho_m is None:
                break
            total_custo += custo_m
            # Retorna à entrada
            caminho_m2, custo_m2 = a_star(masmorras_ordem[idx], pingentes_ordem[idx], entrada_masmorra, {'CC': MASMORRA_COST, 'P': MASMORRA_COST, 'E': MASMORRA_COST}, walkable={'CC', 'P', 'E'})
            if caminho_m2 is None:
                break
            total_custo += custo_m2
            pos = entradas_ordem[idx]
        # Caminho final até Lost Woods
        caminho, custo = a_star(mapa, pos, lost_woods, TERRAIN_COSTS)
        if caminho is None:
            continue
        total_caminho += caminho[1:]
        total_custo += custo
        if total_custo < menor_custo:
            menor_custo = total_custo
            melhor_ordem = ordem
            melhor_caminho = total_caminho

    # Exibe resultado
    print("Melhor ordem de masmorras:",[x+1 for x in melhor_ordem])
    print("Custo total:", menor_custo)
    print("Caminho percorrido (apenas mapa principal):")
    print_mapa(mapa, [p for p in melhor_caminho if p[0] < 42 and p[1] < 42])

if __name__ == "__main__":
    main()