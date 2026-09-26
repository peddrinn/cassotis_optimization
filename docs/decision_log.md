# Decision Log

Este documento registra decisões relevantes do projeto. Não deve ser usado apenas para descrever o que foi implementado; deve registrar **por que** cada escolha foi feita.

Estados possíveis: `CONFIRMADA`, `CONSOLIDADA`, `PENDENTE`, `SUPERADA`.

---

## D001 — Unidade da variável de decisão

**Status:** CONSOLIDADA

**Decisão:** representar \(x_{ip}\) como número de caminhões do minério \(i\) usados na pilha \(p\).

**Alternativa considerada:** representar diretamente massa em kt.

**Motivação:** cada caminhão possui 2 kt e as disponibilidades do enunciado já são dadas em caminhões. A escolha incorpora naturalmente a integralidade e evita uma restrição adicional de múltiplos de 2 kt.

**Impacto:** massa em kt é calculada como \(2x_{ip}\).

---

## D002 — Interpretação de disponibilidade mínima e máxima

**Status:** CONFIRMADA

**Decisão:** os limites são globais sobre as 10 pilhas:

\[
d_i^{min}\le\sum_p x_{ip}\le d_i^{max}.
\]

**Fonte:** esclarecimento explícito da professora. Se um minério tem mínimo 3, pelo menos 3 caminhões desse minério devem ser utilizados no total; eles podem ser concentrados em uma pilha ou distribuídos entre várias.

**Impacto:** disponibilidade não deve ser verificada separadamente por pilha.

---

## D003 — Representação computacional por slots de caminhão

**Status:** CONSOLIDADA

**Decisão:** representar cada pilha por um vetor com \(M_p/2\) posições; cada posição contém um minério e representa um caminhão.

**Alternativa considerada:** armazenar apenas a matriz de contagens \(x_{ip}\).

**Motivação:** o enunciado define N1 e N2 em termos de posições no vetor de composição. A representação por slots torna os movimentos naturais e preserva massa.

**Impacto:** a matriz \(x_{ip}\) continua útil, mas é derivada da solução.

---

## D004 — Tratamento da massa

**Status:** CONSOLIDADA

**Decisão:** preservar massa por construção mantendo fixo o tamanho do vetor de cada pilha.

**Motivação:** não há benefício em explorar estados com massa incorreta quando a representação pode eliminar essa classe de inviabilidade sem reduzir a expressividade da solução.

---

## D005 — Elegibilidade logística

**Status:** CONSOLIDADA

**Decisão:** N1, N2 e futuras vizinhanças devem impedir inserção de minério em grupo para o qual ele não seja elegível sempre que isso puder ser garantido diretamente pelo operador.

**Motivação:** elegibilidade é uma condição discreta simples e pode ser preservada sem introduzir trade-off útil.

---

## D006 — FeT

**Status:** CONSOLIDADA

**Decisão:** manter FeT nos dados, cálculos e visualizações, mas não tratá-lo como restrição ativa na instância de exemplo.

**Motivação:** o enunciado informa limites 0%–100% e declara que FeT não influencia a otimização neste case.

---

## D007 — Política de tratamento de inviabilidade de qualidade e disponibilidade

**Status:** CONSOLIDADA (Entrega 1; revisar com o grupo)

**Escopo:** violações de SiO2, Al2O3 e disponibilidade global.

**Decisão:** regra de viabilidade (dominação por restrições), implementada em `feasibility.feasibility_rule_key` e usada em toda comparação da GVNS:

1. solução viável vence solução inviável;
2. entre viáveis, vence a de menor objetivo;
3. entre inviáveis, vence a de menor \(V(X)\) normalizado (`normalized_violation`); o objetivo desempata.

**Alternativas consideradas:** rejeição pura; penalização \(f+\lambda V\) estática ou dinâmica; reparo; operadores totalmente preservadores; estratégia em duas fases.

**Motivação:**

- a solução inicial da construtiva é inviável (SiO2 ≈ 7,1% nas pilhas do Sinter 1, limite 6,2%), o que descarta a rejeição pura;
- não há coeficiente \(\lambda\) para calibrar, o que evita três calibrações dependentes da escala (custo ~10^7 R$ contra desvios ~1);
- a regra não depende da escala do objetivo, então pode ser reutilizada nas escalarizações da Entrega 2;
- equivale a uma estratégia em duas fases (primeiro reduzir \(V\), depois otimizar \(f\)) sem precisar de uma troca explícita de fase.

**Consequências:** depois de viável, a solução corrente não volta a ser inviável, e a travessia de regiões inviáveis fica limitada (Aula 04, slide 14). A perturbação pode gerar soluções inviáveis, que a VND usa como ponto de partida. \(V(X)\) permanece a soma linear das violações normalizadas (não a soma de quadrados da Aula 04), porque só é usado para ordenar soluções inviáveis entre si.

**Evidência:** nas execuções de calibração (sementes 1001–1003, 100 mil avaliações), todas as execuções dos três objetivos chegaram à região viável, a primeira solução viável entre 298 e 4.963 avaliações. Nas 15 execuções finais (sementes 1–5, 200 mil avaliações), todas terminaram viáveis, com a primeira solução viável entre 256 e 7.540 avaliações.

Ver `docs/feasibility_strategy.md` e `docs/gvns_decisoes.md`.

---

## D008 — Terceira vizinhança N3

**Status:** CONSOLIDADA

**Decisão:** utilizar uma vizinhança de realocação com substituição em cadeia.

O movimento seleciona duas pilhas distintas \(p_a\) e \(p_b\), contendo respectivamente os minérios \(m_x\) e \(m_y\), e um novo minério \(m_z\). O movimento realiza:

\[
p_a: m_x \rightarrow m_z
\]

\[
p_b: m_y \rightarrow m_x
\]

desde que \(m_z\) seja elegível para \(p_a\) e \(m_x\) seja elegível para \(p_b\).

**Alternativas consideradas:** ciclo entre três pilhas, dupla substituição dentro de uma pilha e movimentos guiados diretamente pela medida de inviabilidade \(V(X)\).

**Motivação:** N3 combina, em uma única transição, duas características que aparecem separadamente em N1 e N2: alteração da composição global de minérios e realocação entre pilhas. O movimento pode modificar diretamente \(f_1\), \(f_2\) e \(f_3\), sendo também adequado para reutilização nas etapas multiobjetivo.

A execução coordenada evita depender da aceitação de estados intermediários que seriam necessários ao decompor o movimento em aplicações sucessivas de outras vizinhanças.

**Impacto:** a massa das pilhas e a elegibilidade são preservadas por construção. O consumo global de \(m_x\) permanece inalterado, enquanto o consumo de \(m_y\) diminui em uma unidade e o de \(m_z\) aumenta em uma unidade. Portanto, o movimento pode gerar violações de disponibilidade e qualidade, que deverão ser tratadas pela política definida em D007.

O movimento pode alterar o custo segundo:

\[
\Delta f_1 = 2000(c_z-c_y).
\]

**Implementação:** `algorithms/vizinhancas.py` (`n3_moves`, `sample_n3_move`, `n3_relocate_replace`). Os movimentos são definidos sobre os minérios distintos de cada pilha (ver D014).

---

## D009 — VNS ou GVNS

**Status:** CONSOLIDADA (Entrega 1; revisar com o grupo)

**Decisão:** GVNS (Aula 02, slides 36–38): perturbação P_k seguida de VND sobre N1 → N2 → N3, com troca de vizinhança "melhorou → volta para k=1 / ℓ=1; senão → próxima".

**Alternativas consideradas:** VNS básica com uma única vizinhança de refinamento; RVNS.

**Motivação:** o enunciado exige três vizinhanças. Na GVNS as três participam da busca local, e não só da perturbação. As vizinhanças são complementares: N1 altera o consumo global, N2 só redistribui entre pilhas, N3 faz as duas coisas.

**Implementação:** `algorithms/gvns.py`.

---

## D010 — Critério de parada e orçamento experimental

**Status:** CONSOLIDADA (Entrega 1; revisar com o grupo)

**Decisão:** orçamento fixo de 200.000 avaliações de soluções candidatas por execução, igual para f1, f2 e f3. Não há critério auxiliar. O tempo é registrado como informação complementar.

**Alternativas consideradas:** tempo de parede; número de iterações da GVNS; iterações sem melhoria.

**Motivação:** o número de avaliações não depende da máquina, coincide com o eixo x das curvas de convergência e permite comparação justa entre objetivos. Com cerca de 50 µs por avaliação, cada execução levou de 12 a 35 s.

**Evidência (execuções finais):** da avaliação 100 mil à 200 mil, o melhor valor melhorou no máximo 1,4% (menos de 0,1% em 7 das 15 execuções). Ainda há melhorias pequenas perto do fim do orçamento.

---

## D011 — Reprodutibilidade

**Status:** CONSOLIDADA

**Decisão:** separar fase de calibração de parâmetros da fase de resultados finais e registrar seeds/configurações das execuções finais.

**Motivação:** evitar seleção oportunista de configurações após observar os resultados e permitir reprodução do relatório.
---

## D012 — Separação entre avaliação e objetivo ativo

**Status:** CONSOLIDADA

**Decisão:** a função `evaluate()` calcula simultaneamente \(f_1\), \(f_2\), \(f_3\), qualidade e violações. A função `objective_value()` apenas seleciona qual objetivo será minimizado em uma execução mono-objetivo.

**Motivação:** evitar duplicação de cálculos e desacoplar a definição do problema da metaheurística.

**Impacto:** o mesmo algoritmo poderá ser reutilizado para otimizar \(f_1\), \(f_2\) ou \(f_3\), e a mesma avaliação poderá ser reaproveitada nas etapas multiobjetivo.

---

## D013 — Heurística construtiva baseline

**Status:** CONSOLIDADA

**Decisão:** a solução inicial é construída em duas fases. Primeiro, são atendidas as disponibilidades mínimas globais dos minérios, distribuindo esses caminhões apenas em pilhas elegíveis. Depois, os slots restantes são preenchidos com os minérios elegíveis de menor custo que ainda possuam disponibilidade máxima restante.

**Motivação:** seguir a lógica sugerida no enunciado e garantir, já na construção, massa correta, elegibilidade e limites globais de disponibilidade.

**Impacto:** a solução inicial pode continuar inviável quanto aos limites de SiO₂ e Al₂O₃. A política de tratamento dessas inviabilidades permanece pendente em D007.

**Evidência:** a solução construída tem custo R$ 59,34 mi, f2 = 14,90 e f3 = 7,00, e é inviável em SiO2 nas pilhas do Sinter 1 (≈ 7,1%) e levemente em Al2O3 em P1, P2 e P4. A GVNS chega à região viável a partir dela em todas as execuções (D007).

---

## D014 — Busca local: primeira melhoria, N1 completa, N2/N3 amostradas

**Status:** CONSOLIDADA (Entrega 1; revisar com o grupo)

**Decisão:**

- busca local de primeira melhoria, repetida até não haver movimento de melhoria, com a vizinhança percorrida em ordem aleatória definida pela semente;
- VND na ordem N1 → N2 → N3, da vizinhança menor para a maior;
- N1 é explorada por completo (cerca de 1.100 movimentos distintos);
- N2 (cerca de 3.000 movimentos) e N3 (cerca de 10^5) são exploradas por uma amostra de 500 movimentos a cada passada;
- movimentos definidos sobre os minérios distintos de cada pilha, porque posições com o mesmo minério geram a mesma solução. O conjunto de soluções alcançáveis é o mesmo das definições do enunciado (por posição).

**Alternativas consideradas:** melhor melhoria; exploração completa de N1 e N2; amostragem das três vizinhanças.

**Motivação:** melhor melhoria e exploração completa de N3 consumiriam o orçamento em poucos passos. A amostragem de N2 permite mais iterações da GVNS sem perda de qualidade observável.

**Evidência (calibração, sementes 1001–1003, 100 mil avaliações, média do valor final):**

| Variante | f1 (R$) | f2 | f3 | iterações GVNS (f1) |
|---|---|---|---|---|
| A: N1 e N2 completas, N3 com 500 | 60.326.667 | 2,40616 | 1,44573 | 12–14 |
| **B: N1 completa, N2/N3 com 500 (escolhida)** | **60.313.333** | **2,39516** | **1,44813** | **15–16** |
| C: todas amostradas (300) | 60.320.000 | 2,39565 | 1,44702 | 34–39 |
| D: como B, SHAKE com 2 mov./k e k_max=4 | 60.353.333 | 2,39498 | 1,45098 | 18–19 |

As diferenças são menores que 1%. A variante B foi escolhida por ter o melhor ou quase o melhor resultado em f1 e f2 e por manter um ótimo local verdadeiro em N1.

---

## D015 — Perturbação (SHAKE)

**Status:** CONSOLIDADA (Entrega 1; revisar com o grupo)

**Decisão:** P_k aplica k × 3 movimentos aleatórios, com k = 1..3 (k_max = 3). Cada movimento é sorteado de N1, N2 ou N3 com probabilidade igual. A solução perturbada é avaliada (conta no orçamento) e passada à VND.

**Alternativas consideradas:** um movimento da vizinhança N_k; 2 movimentos por k com k_max = 4 (variante D de D014); reconstrução parcial de pilhas.

**Motivação:** a intensidade cresce com k, seguindo a lógica da VNS. Um único movimento, numa solução de 145 caminhões, seria desfeito pela VND. De 3 a 9 movimentos tiram a solução da bacia atual sem torná-la aleatória. Misturar as vizinhanças perturba tanto o consumo global quanto a distribuição entre pilhas.

---

## D016 — Critério de aceitação

**Status:** CONSOLIDADA (Entrega 1; revisar com o grupo)

**Decisão:** X'' substitui X somente se for estritamente melhor pela regra de D007, com tolerância relativa de 10^-12 para ignorar ruído de ponto flutuante.

**Alternativas consideradas:** aceitar soluções iguais (movimento lateral); aceitação probabilística do tipo recozimento simulado.

**Motivação:** é a aceitação do pseudocódigo da GVNS visto em aula e não introduz parâmetros. A diversificação vem do SHAKE.

---

## D017 — Sementes e separação entre calibração e resultados finais

**Status:** CONSOLIDADA

**Decisão:** calibração com as sementes 1001, 1002 e 1003. Resultados finais com as sementes 1, 2, 3, 4 e 5, fixadas antes de gerar os resultados reportados. O desvio-padrão reportado é o amostral (n−1). A construtiva é determinística, então as execuções diferem apenas pela semente da GVNS.

**Motivação:** aplicar D011 e evitar a escolha de parâmetros com base nos resultados finais.

**Implementação:** `scripts/run_mono_experiments.py`.
