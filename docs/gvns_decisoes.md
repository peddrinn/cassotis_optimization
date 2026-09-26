# GVNS da Entrega 1 — o que foi decidido e por quê

Este texto explica, em linguagem direta, as escolhas feitas na implementação da
metaheurística (`src/cassotis_optimization/algorithms/gvns.py`). O registro
formal de cada decisão, com alternativas e consequências, está em
`docs/decision_log.md` (D007, D009, D010, D014–D017).

Para cada ponto, é indicado o que **o enunciado exige** e o que **é escolha do
grupo**. As escolhas do grupo foram propostas nesta implementação e devem ser
revisadas pelo grupo antes da entrega.

---

## 1. VNS ou GVNS? → GVNS

**Enunciado:** permite VNS ou GVNS.

**Escolha:** GVNS, seguindo o pseudocódigo da Aula 02 (slides 36–38).

**Por quê:**

- O enunciado exige três vizinhanças (N1, N2, N3). Na VNS básica, a busca
  local usa uma única vizinhança; as outras apareceriam só na perturbação.
  Na GVNS, a busca local é uma VND que usa as três de forma sistemática, então
  todas as vizinhanças pedidas realmente participam da intensificação.
- As três vizinhanças fazem coisas diferentes: N1 muda a composição global,
  N2 redistribui entre pilhas sem mudar o consumo global, e N3 faz as duas
  coisas ao mesmo tempo. Um ótimo local em N1 frequentemente não é ótimo local
  em N2 (e vice-versa), e a VND explora exatamente isso.

## 2. Pseudocódigo

```text
GVNS(instância, objetivo f, semente, orçamento):
    X ← CONSTRUTIVA()                      # pode ser inviável em qualidade
    X ← VND(X)
    enquanto houver orçamento de avaliações:
        k ← 1
        enquanto k ≤ k_max:                # k_max = 3
            X'  ← SHAKE(X, k)              # k·3 movimentos aleatórios em N1/N2/N3
            X'' ← VND(X')
            se X'' é melhor que X:         # regra de viabilidade (seção 4)
                X ← X'';  k ← 1
            senão:
                k ← k + 1
    retornar melhor solução avaliada

VND(X):
    ℓ ← 1
    enquanto ℓ ≤ 3:                        # N1 → N2 → N3
        X' ← BUSCA_LOCAL(X, N_ℓ)
        se X' é melhor que X:  X ← X';  ℓ ← 1
        senão:                 ℓ ← ℓ + 1
    retornar X

BUSCA_LOCAL(X, N):                         # primeira melhoria
    repetir
        para cada movimento m em N(X), em ordem aleatória:
            (N1: todos os movimentos;  N2 e N3: amostra de 500 movimentos)
            Y ← aplicar m em X;  avaliar Y   # conta 1 avaliação
            se Y é melhor que X:  X ← Y;  recomeçar
    até nenhum movimento melhorar
    retornar X
```

O orçamento é verificado a cada avaliação; quando ele acaba, a execução para
imediatamente e devolve a melhor solução já avaliada.

## 3. Tratamento de soluções inviáveis → regra de viabilidade

**Enunciado:** cada grupo deve escolher e justificar (rejeição, penalização,
reparo ou operadores que preservem a viabilidade). O enunciado também avisa
que a solução inicial pode ser inviável.

**O que já era garantido pela representação:** massa das pilhas, integralidade
(múltiplos de 2 kt) e elegibilidade. Sobram como possíveis violações: limites
de SiO₂ e Al₂O₃ em cada pilha e disponibilidade mínima/máxima global.

**Escolha:** regra de viabilidade (Aula 02, slides 46–50):

1. solução viável sempre vence solução inviável;
2. entre duas viáveis, vence a de menor objetivo;
3. entre duas inviáveis, vence a de menor violação normalizada V(X)
   (`feasibility.py`); o objetivo só desempata.

**Por quê:**

- **Funciona partindo de solução inviável.** A construtiva gera as pilhas do
  Sinter 1 com SiO₂ ≈ 7,1% (limite 6,2%). Com a regra, a busca primeiro reduz
  V(X) e, ao chegar em V = 0, passa a otimizar o objetivo. Nas 15 execuções
  finais, a primeira solução viável apareceu entre 256 e 7.540 avaliações
  (no máximo 3,8% do orçamento).
- **Não tem parâmetro de penalidade.** Uma penalização F = f + λV exigiria
  calibrar λ para cada objetivo, porque o custo está na casa de 10⁷ R$ e os
  desvios quadráticos na casa de 1. Isso seria três calibrações a mais, e a
  Aula 04 (slide 33) mostra que um λ mal escolhido bloqueia a busca ou a deixa
  presa na região inviável.
- **É reaproveitável na Entrega 2.** Ela não depende da escala do objetivo,
  então continua valendo quando o objetivo passar a ser uma soma ponderada
  normalizada ou quando as restrições ε forem adicionadas.
- **Rejeição pura não serve** porque a solução inicial já é inviável.
- **Reparo** exigiria projetar um procedimento específico de correção de
  qualidade, o que tem risco de dominar o comportamento da busca.

**Limitação conhecida:** depois de viável, a busca não atravessa mais regiões
inviáveis (Aula 04, slide 14). A perturbação compensa em parte: o SHAKE pode
gerar uma solução inviável, e a VND a partir dela pode reencontrar outra região
viável. Isso deve ser discutido no relatório.

## 4. Critério de aceitação → só melhoria estrita

**Enunciado:** não especifica.

**Escolha:** X'' substitui X somente se for estritamente melhor pela regra
acima, como no pseudocódigo da Aula 02. Uma tolerância relativa de 10⁻¹²
evita "melhorias" causadas só por arredondamento de ponto flutuante.

**Por quê:** é a aceitação padrão da VNS/GVNS vista em aula. Ela é simples de
explicar e combina bem com a regra de viabilidade. A diversificação fica a
cargo do SHAKE com intensidade crescente.

## 5. Busca local → primeira melhoria; N1 completa, N2 e N3 amostradas

**Enunciado:** exige a busca local, mas não diz como.

**Escolha:**

- **Primeira melhoria**, com a vizinhança percorrida em ordem aleatória
  (a ordem vem da semente, então a execução é reprodutível).
- **N1 é explorada por completo** (cerca de 1.100 movimentos distintos na
  instância), então o resultado é um ótimo local verdadeiro em N1.
- **N2 (cerca de 3.000 movimentos) e N3 (cerca de 100.000) são amostradas**:
  a cada passada são sorteados 500 movimentos. Se nenhum melhora, considera-se
  ótimo local naquela vizinhança.

**Por quê:**

- Melhor melhoria gastaria a vizinhança inteira a cada passo. Com N3 na casa
  de 10⁵ movimentos, isso consumiria o orçamento inteiro em poucos passos.
- Explorar N3 por completo só para confirmar ótimo local custaria mais do que
  todo o resto da execução.
- **Evidência (calibração com as sementes 1001–1003, orçamento de 100 mil
  avaliações):** explorar N2 por completo ou por amostragem deu resultados
  praticamente iguais (diferença < 1%). A amostragem permite mais iterações da
  GVNS no mesmo orçamento. A tabela está em D014 no `decision_log.md`.

**Detalhe de implementação:** posições que contêm o mesmo minério numa pilha
geram exatamente a mesma solução quando trocadas. Por isso os movimentos são
definidos sobre os minérios distintos de cada pilha, e não sobre cada posição.
O conjunto de soluções alcançáveis é o mesmo do enunciado, só sem vizinhos
repetidos.

## 6. Perturbação (SHAKE) → k·3 movimentos aleatórios

**Enunciado:** exige perturbação, mas não diz qual.

**Escolha:** a perturbação P_k aplica k × 3 movimentos aleatórios, com
k = 1, 2, 3 (ou seja, 3, 6 ou 9 movimentos). Cada movimento é sorteado de
N1, N2 ou N3 com a mesma probabilidade.

**Por quê:**

- A Aula 02 separa as estruturas de perturbação P_k das estruturas de
  refinamento N_ℓ. Aqui a intensidade cresce com k, como pede a lógica da VNS:
  se perturbações pequenas não levam a uma solução melhor, tenta-se uma maior.
- Um único movimento é pequeno demais: a solução tem 145 caminhões, e a VND
  desfaria o movimento na primeira passada. Com 3 a 9 movimentos, a solução
  perturbada sai da bacia do ótimo local atual sem virar uma solução aleatória.
- Misturar N1, N2 e N3 permite que a perturbação altere tanto a composição
  global quanto a distribuição entre pilhas.
- Na calibração, a variante com 2 movimentos por k e k_max = 4 não foi melhor.

## 7. Critério de parada → 200 mil avaliações

**Enunciado:** não especifica; pede curvas de convergência em função de
avaliações ou iterações.

**Escolha:** orçamento fixo de 200.000 avaliações de soluções candidatas por
execução, igual para f1, f2 e f3.

**Por quê:**

- Contar avaliações não depende da máquina (tempo depende). Assim as curvas
  e os resultados são comparáveis entre objetivos e entre computadores do grupo.
- O eixo x das curvas de convergência fica exatamente igual ao critério de
  parada.
- Cada avaliação custa cerca de 50 µs. Nas execuções finais, cada uma levou
  de 12 a 35 s, e as 15 juntas levaram cerca de 4 minutos.
- A maior parte do ganho acontece cedo: da avaliação 100 mil até a 200 mil,
  o melhor valor melhorou no máximo 1,4% (em 7 das 15 execuções, menos de
  0,1%). Ainda aparecem melhorias pequenas perto do fim, então um orçamento
  maior poderia ajudar marginalmente. Isso vale mencionar no relatório.

O tempo de execução é registrado como informação complementar.

## 8. Protocolo experimental

**Enunciado:** 5 execuções por objetivo, com mínimo, desvio-padrão e máximo,
as 5 curvas sobrepostas e uma figura da melhor solução.

**Escolhas:**

- As sementes finais são 1, 2, 3, 4 e 5, fixadas antes de gerar os
  resultados. A calibração usou outro conjunto de sementes (1001–1003), para
  não escolher parâmetros olhando os resultados finais (D011).
- A heurística construtiva é determinística, então as 5 execuções partem da
  mesma solução inicial e diferem pela semente, que controla a ordem da busca
  local, as amostras e a perturbação.
- O desvio-padrão é o amostral (n − 1).
- A curva mostra a **melhor solução viável encontrada até aquela avaliação**.
  O ponto inicial de cada curva marca o momento em que a execução ficou viável.

Para reproduzir:

```bash
python scripts/run_mono_experiments.py            # gera results/mono/
```

Cada execução salva, em `results/mono/runs/*.json`:

- versão do código, instância, objetivo e semente;
- parâmetros e orçamento;
- valores finais de f1, f2, f3 e viabilidade;
- tempo de execução;
- composição da melhor solução;
- curva de convergência.

## 9. Parâmetros finais

| Parâmetro | Valor | Origem |
|---|---|---|
| Orçamento | 200.000 avaliações | D010 |
| k_max | 3 | D015 |
| Movimentos por k no SHAKE | 3 | D015 |
| Ordem da VND | N1 → N2 → N3 | D014 |
| Vizinhanças exploradas por completo | N1 | D014 |
| Tamanho da amostra (N2, N3) | 500 | D014 |
| Aceitação | melhoria estrita (regra de viabilidade) | D016 |
| Sementes finais | 1, 2, 3, 4, 5 | D017 |

## 10. Observação sobre a instância

A disponibilidade máxima total é de 166 caminhões para 145 necessários. Por
isso, na otimização de f2, os minérios com pouco SiO₂ (M1, M2, M6, M7, M11,
M18) terminam todos no limite máximo, e as pilhas ficam com SiO₂ entre 5,9% e
6,1%, acima dos alvos de 5,55% e 5,50%. Isso vem da escassez desses minérios,
não de uma falha da busca, e vale comentar no relatório.

## 11. Resultados das execuções finais

Sementes 1–5, 200 mil avaliações (`results/mono/summary.md`):

| Objetivo | viáveis | mínimo | desvio-padrão | máximo |
|---|---|---|---|---|
| f1 (R$) | 5/5 | 60.020.000 | 37.417 | 60.100.000 |
| f2 | 5/5 | 2,37295 | 0,01806 | 2,40594 |
| f3 | 5/5 | 1,43540 | 0,00265 | 1,44146 |

Em f2, as execuções terminam em dois patamares (≈ 2,373 em três sementes e
≈ 2,406 em duas). Isso indica ótimos locais distintos que a perturbação não
conseguiu conectar dentro do orçamento, e é um ponto a discutir no relatório.
