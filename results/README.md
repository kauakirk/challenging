# Results

| Arquivo | Descrição | Status |
|---|---|---|
| `agentcore_direct_eval_results.json` | Avaliação direta via runtime logs — 7 cenários com scores reais | ✅ Dados reais |
| `agentcore_eval_results.json` | Execução do OnDemandEvaluationDatasetRunner — 20 cenários | ⚠️ Credenciais SSO expiraram (~20 min) durante execução longa |
| `red_team_log.json` | Log completo da campanha de red teaming — 15 tentativas | ✅ Completo |
| `red_team_findings.md` | Tabela de achados do red teaming com evidências | ✅ Completo |
| `custom_evaluator_results.json` | Resultados do avaliador customizado EspecificacaoComFonte | Gerado ao executar `custom_evaluator.py` |

> **Nota:** O ambiente de laboratório usa credenciais SSO temporárias com expiração de ~20 minutos.
> Para execuções longas (20 cenários × 180s de delay = ~60 min), as credenciais expiram antes do fim.
> Use `agentcore_direct_eval_results.json` como referência principal dos scores AgentCore.
