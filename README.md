# Cassotis Optimization — Teoria da Decisão UFMG 2026/2

Projeto da disciplina **Teoria da Decisão** para o case **Otimização do Custo e Qualidade de Pilhas de Minério**.

O objetivo é desenvolver, documentar e avaliar uma solução baseada em VNS/GVNS para as etapas mono-objetivo e multiobjetivo e, posteriormente, aplicar métodos de apoio multicritério à decisão.

## Estado atual

Este repositório está na **M0 — especificação formal e infraestrutura do projeto**.

Já estão consolidados:

- variável de decisão em número de caminhões;
- capacidade fixa de 2 kt por caminhão;
- disponibilidade mínima e máxima global por minério, considerando as 10 pilhas;
- representação computacional por posições de caminhões nas pilhas;
- massa preservada por construção;
- elegibilidade preservada pelos operadores de vizinhança;
- formulação dos três objetivos;
- FeT mantido no domínio, mas não ativo como restrição na instância de exemplo.

Ainda **não** estão consolidados:

- política final de tratamento de inviabilidade;
- terceira vizinhança N3;
- escolha entre VNS e GVNS;
- organização final da busca local;
- perturbação;
- critérios de aceitação e parada;
- parâmetros experimentais.

As decisões e seus status são mantidos em [`docs/decision_log.md`](docs/decision_log.md).

## Fonte do problema

A especificação principal é o enunciado do case da disciplina. Os dados em `data/example_instance/` correspondem ao **exemplo apresentado no anexo do enunciado** e não devem ser confundidos com uma eventual instância definitiva fornecida posteriormente.

Há também uma clarificação da professora sobre disponibilidade: os limites mínimo e máximo de cada minério são globais sobre todas as pilhas. Se um minério tiver disponibilidade mínima 3, devem ser utilizados pelo menos 3 caminhões desse minério no total, distribuídos livremente entre as 10 pilhas, respeitando as demais restrições.

## Estrutura

```text
.
├── AGENTS.md
├── CONTRIBUTING.md
├── README.md
├── pyproject.toml
├── data/
│   ├── README.md
│   └── example_instance/
│       ├── groups.csv
│       ├── minerals.csv
│       └── piles.csv
├── docs/
│   ├── decision_log.md
│   ├── deliverables_checklist.md
│   ├── experiment_protocol.md
│   ├── feasibility_strategy.md
│   ├── problem_formulation.md
│   └── source_notes.md
├── src/
│   └── cassotis_optimization/
│       ├── __init__.py
│       ├── domain.py
│       ├── evaluator.py
│       ├── io.py
│       ├── solution.py
│       ├── validation.py
│       ├── algorithms/
│       ├── mcda/
│       └── multiobjective/
├── scripts/
│   └── validate_instance.py
├── tests/
│   ├── test_evaluator.py
│   └── test_instance.py
├── app/
├── notebooks/
└── results/
```

## Preparação do ambiente

Requer Python 3.11 ou superior.

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev,app]"
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev,app]"
```

## Validação inicial

```bash
python scripts/validate_instance.py
pytest
```

## Regra de desenvolvimento

Nenhuma decisão de modelagem ou algoritmo deve ser alterada silenciosamente. Mudanças relevantes devem ser registradas em `docs/decision_log.md` com motivação, alternativas consideradas e impacto esperado.

A lógica central deve permanecer em `src/`. Notebooks e Streamlit devem consumir essa implementação, e não recriar fórmulas ou regras paralelas.
