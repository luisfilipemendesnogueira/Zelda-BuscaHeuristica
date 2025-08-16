# Inteligência Artificial
## Trabalho Prático - BUSCA HEURÍSTICA
### 1. Descrição do Problema
Após matar o rei de Hyrule, o mago Agahnim está mantendo a princesa Zelda
prisioneira e pretende romper o selo que mantem o malvado Ganon aprisionado no
Dark World.
Link é o único guerreiro capaz de vencer o mago Agahnim, salvar a princesa Zelda e
trazer a paz para o reino de Hyrule. Porém, a única arma forte o suficiente para
derrotar o mago Agahnim é a legendaria Master Sword (**Figura 1**), que encontra-se
presa em um pedestal em Lost Woods.
Para provar que é digno de empunhar a Master Sword, Link deve encontrar e reunir
os três Pingentes da Virtude: coragem, poder e sabedoria (**Figura 2**). Os três
pingentes encontram-se espalhados pelo reino de Hyrule, dentro de perigosas
Masmorras.
O seu objetivo é encontrar os três pingentes da virtude e em seguida ir para Lost
Woods procurar a legendaria Master Sword

<img width="839" height="328" alt="image" src="https://github.com/user-attachments/assets/febeaa52-fa1b-4f8e-a3a3-ac5f56f51aff" />

### 2. Implementação
O Trabalho consiste em implementar um agente capaz de locomover-se
autonomamente pelo reino de Hyrule, explorar as perigosas masmorras e reunir os
três Pingentes da Virtude. Para isso, você deve utilizar **o algoritmo de busca
heurística A***.
O agente deve ser capaz de calcular automaticamente a melhor rota para reunir os
três pingentes da virtude e ir para Lost Woods, onde está localizada a Master
Sword.
O mapa do reino de Hyrule é mostrado na **Figura 3**.

<img width="740" height="802" alt="image" src="https://github.com/user-attachments/assets/a6c49c95-c546-4798-9f4e-a4fc638505e7" />

O reino de Hyrule é formado por **5 tipos de terrenos**: grama (região verde claro),
água (região azul), montanha (região marrom), areia (região marrom claro) e
floresta (região verde escuro).
Os custos para passar por cada tipo de terreno são os seguintes:
- **Grama** – Custo: +10
- **Areia** – Custo: +20
- **Floresta** – Custo: +100
- **Montanha** – Custo: +150
- **Água** – Custo: +180

Os **três pingentes da virtude** estão localizados dentro de **Masmorras**, as quais
estão identificadas no mapa pelos portões de entrada. O mapa de cada Masmorra
é mostrado na **Figura 4**, onde o portão marca o ponto de entrada/saída e o
pingente identifica a posição do pingente da virtude.

<img width="1289" height="522" alt="image" src="https://github.com/user-attachments/assets/e714a884-4205-4c18-8b22-17d47f386c4b" />

Dentro das Masmorras, somente é possível caminhar pelas regiões mais claras
identificadas no mapa. O custo para andar nesse tipo de terreno é de +10.
Link inicia sua jornada na **posição [25, 28]** e termina após reunir os três pingentes
da virtude e chegar até a entrada de Lost Woods (**posição [7, 6]**), onde ele poderá
encontrar a Master Sword. A melhor rota para cumprir essa missão é a rota de
menor custo levando em consideração o terreno.

### 3. Informações Adicionais
- O mapa principal deve ser representado por uma matriz 42 x 42 (igual à
mostrada na Figura 3). As Masmorras também devem ser representadas por
matrizes de tamanho 28 x 28 (iguais às mostradas na Figura 4).
- O agente sempre **inicia** a jornada na casa do Link (ponto onde está o Link no
mapa [25, 28]) e sempre **termina** a sua jornada ao chegar à entrada de Lost
Woods (posição [7, 6]).
- Ao entrar em uma **Masmorra**, o agente deve encontrar o melhor caminho até o
pingente e depois retornar a entrada para sair da Masmorra e retornar para o
mapa principal.
- Os pingentes podem ser coletados **em qualquer ordem**. Porém, ordens
diferentes vão resultaram em custos totais diferentes.
- O agente não pode andar na diagonal, somente na **vertical** e na **horizontal**.
- Deve existir uma maneira de **visualizar os movimentos** do agente, mesmo que
a interface seja bem simples. Podendo até mesmo ser uma matriz desenhada e
atualizada no console
- **Os mapas devem ser configuráveis**, ou seja, deve ser possível modificar o tipo
de terreno em cada local. O mapa pode ser lido de um arquivo de texto ou
deve ser facilmente editável no código.
- O programa deve exibir o **custo do caminho percorrido** pelo agente enquanto
ele se movimenta pelo mapa e também o **custo final** ao terminar a execução.
- O programa pode ser implementado em qualquer linguagem.


### 4. Dicas
Existem pelo menos duas estratégias para resolver o problema de busca neste
trabalho:

a) **Múltiplas Buscas**: Divide-se o processo de busca em pequenas etapas,
inicialmente realiza-se uma busca para encontrar o melhor caminho para
chegar à primeira Masmorra. Ao entrar na Masmorra realiza-se uma nova
busca para encontrar o melhor caminho dentro da Masmorra para chegar até o
Pingente. Ao sair da Masmorra, busca-se o melhor caminho até a próxima
Masmorra e repete-se o processo até chegar ao destino final.

b) **Busca Única**: Realiza-se uma única busca levando em consideração todos os
pingentes e os mapas das Masmorras. Dessa forma o agente conhecerá todos
os passos que ele deve realizar antes mesmo de iniciar a sua jornada.
Note que este problema é semelhante ao problema do Caixeiro Viajante. É
necessário encontrar a melhor rota para visitar todos os membros do grupo uma
única vez. No trabalho não é obrigatória a resolução deste problema, mas é a única
maneira de garantir o melhor custo.
Implemente a função de busca de uma forma genérica, pois pode ser necessário
executá-la múltiplas vezes para diferentes destinos

Note que este problema é semelhante ao problema do **Caixeiro Viajante**. É
necessário encontrar a melhor rota para visitar todos os membros do grupo uma
única vez. No trabalho não é obrigatória a resolução deste problema, mas é a única
maneira de garantir o melhor custo.
Implemente a função de busca de uma forma genérica, pois pode ser necessário
executá-la múltiplas vezes para diferentes destinos.

### 5. Autores
-  Luis Filipe
-  Kaique Rennan
