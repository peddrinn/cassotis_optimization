# Contribuindo

O objetivo do fluxo de colaboração é preservar rastreabilidade das decisões e reprodutibilidade dos resultados.

## Fluxo sugerido

Use branches curtas, por exemplo:

```text
feature/evaluator
feature/constructive
feature/neighborhood-n1
experiment/feasibility-policy
docs/model-formulation
```

Antes de integrar alterações:

```bash
pytest
ruff check .
```

Mudanças que alterem modelagem, algoritmo, parâmetros finais ou interpretação do problema devem atualizar `docs/decision_log.md`.

Não incluir arquivos grandes de resultados brutos no Git sem necessidade. Resultados finais selecionados devem ser reproduzíveis por scripts e acompanhados da configuração que os gerou.

## Commits

Prefira commits com escopo claro, por exemplo:

```text
docs: formalize problem and confirmed assumptions
feat: add instance loader and validation
feat: implement N1 neighborhood
test: cover quality constraint violations
experiment: compare feasibility handling policies
```
