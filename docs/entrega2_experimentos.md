# Entrega 2 — executor experimental

Esta rotina executa a grade registrada em `data/protocolo_entrega2.json`, preservando os modos mono-objetivo da Entrega 1.

## Como executar (raiz do repositório)

```bash
python -m pip install -e .
python -m pytest -q
python scripts/run_multi_experiments.py --phase pilot --dry-run
python scripts/run_multi_experiments.py --phase pilot --max-runs 2 --budget 3000 --out results/multi_smoke
python scripts/run_multi_experiments.py --phase pilot
```

Os resultados do piloto ficam em `results/multi_pilot/`; o script retoma execuções anteriores pelo `config_hash` e rejeita resultados existentes de configurações diferentes. O processo pode ser interrompido e repetido sem perder os arquivos por seed já gravados.

**Antes da fase oficial:** inspecionar `analysis.json`, `summary.csv` e as figuras; documentar problemas e eventuais ajustes na D021; alterar `status` do protocolo para `CONGELADO` em novo commit. Somente então executar:

```bash
python scripts/run_multi_experiments.py --phase final
```

O executor **não permite** reduzir o orçamento ou executar somente parte da grade na fase oficial. O mesmo protocolo fixa seeds 2021–2025 e 200.000 avaliações, totalizando 160 execuções GVNS, desde que ambas as abordagens estejam selecionadas.

## Artefatos

- `runs/<run_id>.json`: valores originais/normalizados, objetivo escalar, as duas condições de factibilidade, violação, parâmetro, composição, histórico e informações de reprodutibilidade.
- `summary.csv`: um registro por GVNS.
- `pareto_weighted_sum.csv`, `pareto_epsilon_restricted.csv`: vetores não dominados em **três** objetivos originais, com a procedência das seeds/configurações.
- `pareto_<metodo>_f1_f2.png`, `..._f1_f3.png`, `..._f2_f3.png`: seis projeções bidimensionais dos pontos filtrados em 3D.
- `analysis.json`: cobertura de factibilidade por configuração, número de soluções e pontos não dominados.
- `manifest.json`: protocolo, localização da instância, versão e integridade dos resultados.

Para o ε-restrito, `scalar_feasible` inclui a factibilidade original **e** os limites ε; `original_feasible` verifica somente as restrições físicas e químicas. Não considerar soluções apenas originalmente factíveis como resultados da abordagem ε.

A frente de Pareto é estimada a partir da coleção **das melhores soluções finais** de cada configuração e seed. Não há garantia de Pareto-otimalidade global. Pontos repetidos no gráfico são unificados, preservando seus `run_ids` completos em CSV.

## Regras de execução

- Rodadas exploratórias e finais não se misturam; usar pastas diferentes para smoke e piloto completo.
- As execuções têm avaliação por orçamento, não tempo como condição de parada.
- As duas abordagens usam o mesmo número de configurações e seeds, mas podem apresentar tempos diferentes.
- Recalcular dominância sempre com os três objetivos **originais** e aplicar as projeções depois, não o contrário.
- Mudanças em pesos, epsilons, seeds ou orçamento após iniciar o piloto exigem registrar uma nova versão do protocolo; a assinatura dos resultados auxilia a detectar inconsistência.
