# AGENTS.md

Este arquivo orienta revisores humanos e agentes/LLMs que trabalhem neste repositório.

## Prioridade das fontes

Ao analisar ou modificar o projeto, use esta ordem de precedência:

1. enunciado oficial do case;
2. esclarecimentos explícitos da professora;
3. `docs/decision_log.md`;
4. `docs/problem_formulation.md`;
5. implementação e testes.

Se código e documentação divergirem, não escolha silenciosamente um deles. Identifique a divergência.

## Regras para decisões

Não transformar uma questão pendente em decisão definitiva sem registrar a mudança.

Toda decisão relevante de modelagem, metaheurística, tratamento de inviabilidade, parametrização, normalização, método multicritério ou protocolo experimental deve ser registrada em `docs/decision_log.md`.

Cada registro deve indicar:

- status;
- decisão;
- alternativas consideradas;
- motivação;
- consequências;
- evidência experimental, quando existir.

## Separação entre requisito e escolha do grupo

Sempre distinguir:

- o que é exigido pelo enunciado;
- o que foi confirmado pela professora;
- o que é decisão do grupo;
- o que ainda está pendente.

Não justificar escolhas do grupo como se fossem exigências do enunciado.

## Reprodutibilidade

Resultados experimentais finais devem registrar, no mínimo:

- versão do código;
- instância usada;
- objetivo/configuração;
- seed;
- orçamento/critério de parada;
- parâmetros da metaheurística;
- valor final dos objetivos;
- viabilidade;
- tempo de execução, quando medido.

## Arquitetura

A implementação de custo, qualidade, restrições e avaliação deve existir em um único núcleo reutilizável.

Não duplicar fórmulas em notebooks, Streamlit, algoritmos mono-objetivo e algoritmos multiobjetivo.

## Estado de decisões relevantes

Consolidadas:

- variável de decisão: número de caminhões por minério e pilha;
- capacidade de caminhão: 2 kt;
- disponibilidade mínima/máxima: global nas 10 pilhas;
- massa das pilhas: preservada pela representação;
- elegibilidade: deve ser preservada pelos operadores sempre que aplicável;
- FeT: calculado/armazenado, mas restrição não ativa na instância de exemplo.

Pendente:

- política final de inviabilidade;
- N3;
- VNS ou GVNS;
- busca local;
- perturbação;
- aceitação;
- parada;
- parâmetros.

Antes de recomendar qualquer uma dessas escolhas, consultar `docs/feasibility_strategy.md` e `docs/decision_log.md`.
