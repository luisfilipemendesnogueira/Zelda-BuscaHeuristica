"""
Módulo de pathfinding para o projeto Zelda.
Contém leitura de mapas, implementação A* e utilitários para
exibir caminhos no terminal.
"""

import heapq
from itertools import permutations

# Custos dos terrenos
TERRAIN_COSTS = {
    "G": 10,   # Grama
    "S": 20,   # Areia
    "F": 100,  # Floresta
    "M": 150,  # Montanha
    "A": 180,  # Água
    "LW": 10,  # Lost Woods (entrada especial)
    "MS": 10,  # Master Sword
    "MA": 20,  # Masmorra (entrada)
    "M1": 20,  # Entrada Masmorra 1
    "M2": 20,  # Entrada Masmorra 2
    "M3": 20,  # Entrada Masmorra 3
}

MASMORRA_COST = 10  # Caminho claro dentro das masmorras


def ler_mapa(path, size):
    """Lê um mapa de arquivo texto e retorna uma matriz (lista de listas).

    Cada linha do arquivo deve conter células separadas por vírgula.
    Retorna uma matriz vazia de tamanho `size` em caso de arquivo não encontrado.
    """
    mapa = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    mapa.append([x.strip() for x in linha.split(",")])
    except FileNotFoundError:
        print(f"Aviso: Arquivo '{path}' não encontrado. O programa pode falhar.")
        # Retorna uma "matriz vazia" com o número de linhas esperado,
        # para manter compatibilidade com quem chama ler_mapa.
        return [[] for _ in range(size)]

    if len(mapa) != size and len(mapa) > 0:
        raise ValueError(f"Mapa {path} não tem tamanho {size}x{size}")
    return mapa


def print_mapa(mapa, caminho=None):
    """Imprime um mapa no terminal com o caminho destacado (se fornecido)."""
    caminho_set = set(caminho) if caminho else set()
    for i, linha in enumerate(mapa):
        out = ""
        for j, cel in enumerate(linha):
            if (i, j) in caminho_set:
                # Usando código de cor ANSI para Amarelo no terminal
                out += "\033[93mL\033[0m  "
            else:
                out += f"{cel:<2} "
        print(out)
    print()


def heuristica(a, b):
    """Distância de Manhattan (sem diagonais)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def vizinhos(pos, size):
    """Retorna vizinhos válidos (vertical/horizontal) para uma posição."""
    x, y = pos
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size:
            yield (nx, ny)


def a_star(mapa, start, goal, terrain_costs, walkable=None):
    """Busca A* genérica que retorna (caminho, custo) ou (None, inf)."""
    size = len(mapa)
    if not (
        0 <= start[0] < size
        and 0 <= start[1] < len(mapa[0])
        and 0 <= goal[0] < size
        and 0 <= goal[1] < len(mapa[0])
    ):
        return None, float("inf")

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristica(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            caminho = [current]
            while current in came_from:
                current = came_from[current]
                caminho.append(current)
            caminho.reverse()
            return caminho, g_score.get(goal, 0)

        for neighbor in vizinhos(current, size):
            x, y = neighbor
            cel = mapa[x][y]
            if walkable and cel not in walkable:
                continue
            cost = terrain_costs.get(cel, 9999)
            tentative_g = g_score.get(current, float("inf")) + cost
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristica(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None, float("inf")


def main():
    """Exemplo de execução: lê mapas e calcula melhor ordem de masmorras."""
    # Lê mapas
    mapa = ler_mapa("Mapa.txt", 42)
    masmorra1 = ler_mapa("Masmorra 1.txt", 28)
    masmorra2 = ler_mapa("Masmorra 2.txt", 28)
    masmorra3 = ler_mapa("Masmorra 3.txt", 28)

    if not all(m for m in [mapa, masmorra1, masmorra2, masmorra3]):
        print("Erro: Um ou mais arquivos de mapa não puderam ser lidos. Encerrando.")
        return

    # Localiza pontos de interesse no mapa
    start = next((i, j) for i, r in enumerate(mapa) for j, c in enumerate(r) if c == "L")
    lost_woods = next(
        (i, j) for i, r in enumerate(mapa) for j, c in enumerate(r) if c == "LW"
    )
    master_sword = next(
        (i, j) for i, r in enumerate(mapa) for j, c in enumerate(r) if c == "MS"
    )
    try:
        entrada1 = next((i, j) for i, r in enumerate(mapa) for j, c in enumerate(r) if c == "M1")
        entrada2 = next((i, j) for i, r in enumerate(mapa) for j, c in enumerate(r) if c == "M2")
        entrada3 = next((i, j) for i, r in enumerate(mapa) for j, c in enumerate(r) if c == "M3")
        entradas = [entrada1, entrada2, entrada3]
    except StopIteration as exc:
        raise ValueError("Erro: Não foi possível encontrar as entradas M1, M2 e M3 "
                         "no Mapa.txt.") from exc

    if start is None or lost_woods is None or len(entradas) < 3:
        raise ValueError("Não foi possível encontrar todos os pontos de interesse no mapa.")

    pingentes = [
        next((i, j) for i, r in enumerate(m) for j, c in enumerate(r) if c == "P")
        for m in [masmorra1, masmorra2, masmorra3]
    ]

    menor_custo = float("inf")
    melhor_ordem = None
    melhor_caminho = None
    melhor_percurso_masmorras = []

    for ordem in permutations([0, 1, 2]):
        pos = start
        total_caminho = []
        total_custo = 0
        percurso_masmorras_atual = []

        mapas_ordenados = [masmorra1, masmorra2, masmorra3]
        entradas_ordem = [entradas[i] for i in ordem]
        pingentes_ordem = [pingentes[i] for i in ordem]
        masmorras_ordem = [mapas_ordenados[i] for i in ordem]

        caminho_inviavel = False
        for idx in range(3):
            caminho, custo = a_star(mapa, pos, entradas_ordem[idx], TERRAIN_COSTS)
            if caminho is None:
                caminho_inviavel = True
                break

            # Usando a lógica original de concatenação de listas que é mais segura
            if total_caminho:
                total_caminho += caminho[1:]
            else:
                total_caminho += caminho
            total_custo += custo

            entrada_masmorra = next(
                (ii, jj)
                for ii, rr in enumerate(masmorras_ordem[idx])
                for jj, cc in enumerate(rr)
                if cc == "E"
            )

            custos_dungeon = {"CC": MASMORRA_COST, "P": MASMORRA_COST, "E": MASMORRA_COST}
            walkable_dungeon = {"CC", "P", "E"}

            caminho_m, custo_m = a_star(
                masmorras_ordem[idx],
                entrada_masmorra,
                pingentes_ordem[idx],
                custos_dungeon,
                walkable_dungeon,
            )
            if caminho_m is None:
                caminho_inviavel = True
                break

            caminho_m2 = caminho_m[::-1]
            custo_m2 = custo_m

            total_custo += custo_m + custo_m2

            percurso_masmorras_atual.append(
                {
                    "id": ordem[idx] + 1,
                    "mapa": masmorras_ordem[idx],
                    "custo_total": custo_m + custo_m2,
                    "caminho_ida": caminho_m,
                    "caminho_volta": caminho_m2,
                }
            )
            pos = entradas_ordem[idx]

        if caminho_inviavel:
            continue

        # Etapa 1: Da última masmorra para Lost Woods
        caminho_lw, custo_lw = a_star(mapa, pos, lost_woods, TERRAIN_COSTS)
        if caminho_lw is None:
            continue

        total_caminho += caminho_lw[1:]
        total_custo += custo_lw

        # Etapa 2: De Lost Woods para a Master Sword
        caminho_ms, custo_ms = a_star(mapa, lost_woods, master_sword, TERRAIN_COSTS)
        if caminho_ms is None:
            continue

        total_caminho += caminho_ms[1:]
        total_custo += custo_ms

        if total_custo < menor_custo:
            menor_custo = total_custo
            melhor_ordem = ordem
            melhor_caminho = total_caminho
            melhor_percurso_masmorras = percurso_masmorras_atual

    # Exibe resultado
    print("=" * 40)
    print("         RESULTADO DA BUSCA")
    print("=" * 40)
    print(f"Melhor ordem de masmorras: {[x+1 for x in melhor_ordem]}")
    print(f"Custo total da jornada: {menor_custo}")
    print("\nCaminho percorrido (mapa principal):")
    print_mapa(mapa, melhor_caminho)

    print("\n" + "=" * 40)
    print("   Detalhes do Percurso nas Masmorras")
    print("=" * 40)

    for masmorra_info in melhor_percurso_masmorras:
        print(f"\n--- Masmorra {masmorra_info['id']} ---")
        print(f"Custo total na masmorra: {masmorra_info['custo_total']}")

        print("\nCaminho de ida (Entrada -> Pingente):")
        print_mapa(masmorra_info["mapa"], masmorra_info["caminho_ida"])

        print("\nCaminho de volta (Pingente -> Entrada):")
        print_mapa(masmorra_info["mapa"], masmorra_info["caminho_volta"])


if __name__ == "__main__":
    main()
