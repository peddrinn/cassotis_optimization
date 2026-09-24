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

## Decisões pendentes

Ainda é necessário definir:

- orçamento em número de avaliações;
- critérios auxiliares de parada;
- seeds finais;
- parâmetros de VNS/GVNS;
- frequência de registro da curva de convergência;
- política de inviabilidade;
- protocolo de calibração.

## Convenção para curvas

A curva principal deverá usar no eixo x o número acumulado de avaliações de soluções candidatas sempre que possível. Isso reduz a dependência da máquina usada e facilita comparação entre configurações.

Tempo de execução deve ser mantido como informação complementar.

## Entrega 2

A normalização dos objetivos deverá usar referências obtidas na Entrega 1, conforme exigido no enunciado.

O protocolo específico de pesos, valores de epsilon e geração das soluções não dominadas será definido somente depois de consolidar os resultados mono-objetivo.

## Entrega 3

Os métodos multicritério e a análise de sensibilidade terão protocolo próprio. Nenhum peso de decisão deve ser escolhido silenciosamente ou apresentado como consequência da otimização.
