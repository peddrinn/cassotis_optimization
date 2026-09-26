# Protocolo experimental

Este documento separa requisitos do enunciado de decisões experimentais ainda pendentes.

## Entrega 1 — requisitos já definidos

Para cada objetivo \(f_1\), \(f_2\) e \(f_3\):

- executar o método estocástico 5 vezes;
- apresentar mínimo, desvio-padrão e máximo dos valores finais;
- apresentar as 5 curvas de convergência sobrepostas;
- apresentar uma visualização da melhor solução encontrada.

## Regras de reprodutibilidade adotadas

Resultados finais devem registrar:

```text
run_id
git_commit
instance
objective
seed
algorithm
parameters
stopping_rule
evaluation_budget
runtime_seconds
feasible
f1
f2
f3
total_violation
```

As seeds das execuções finais serão fixadas antes da produção dos resultados reportados.

Calibração de parâmetros deve ser separada do conjunto de execuções finais.

## Decisões da Entrega 1

- orçamento: 200.000 avaliações por execução, sem critério auxiliar (D010);
- sementes finais: 1–5; calibração com 1001–1003 (D017);
- parâmetros da GVNS: D014–D016;
- política de inviabilidade: regra de viabilidade (D007);
- curva de convergência: registrada a cada melhoria da melhor solução encontrada;
- calibração: comparação de 4 variantes com 3 sementes e 100 mil avaliações (tabela em D014).

Execução: `python scripts/run_mono_experiments.py`.

## Convenção para curvas

A curva principal deverá usar no eixo x o número acumulado de avaliações de soluções candidatas sempre que possível. Isso reduz a dependência da máquina usada e facilita comparação entre configurações.

Tempo de execução deve ser mantido como informação complementar.

## Entrega 2

A normalização dos objetivos deverá usar referências obtidas na Entrega 1, conforme exigido no enunciado.

O protocolo específico de pesos, valores de epsilon e geração das soluções não dominadas será definido somente depois de consolidar os resultados mono-objetivo.

## Entrega 3

Os métodos multicritério e a análise de sensibilidade terão protocolo próprio. Nenhum peso de decisão deve ser escolhido silenciosamente ou apresentado como consequência da otimização.
