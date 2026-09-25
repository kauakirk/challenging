# Evidências - MotoAssist Challenge 02

Esta pasta contém os logs, resultados e evidências principais do projeto MotoAssist.

## Estrutura

### 1. Avaliações
- `agentcore_evaluation_results.json` - Resultados completos AgentCore Evaluations
- `deepeval_test_results.json` - Resultados DeepEval pytest
- `evaluation_comparison.md` - Comparação entre as duas frentes

### 2. Red Teaming
- `red_team_complete_log.json` - Log completo de todas as 15 tentativas
- `vulnerabilities_summary.md` - Resumo das vulnerabilidades encontradas
- `critical_findings.md` - Detalhes dos achados V01 e V02

### 3. Datasets e Configurações
- `golden_dataset.json` - Dataset completo com 20 casos de teste
- `system_prompt_v1.md` - Prompt baseline original
- `system_prompt_v2.md` - Prompt corrigido pós red teaming

### 4. Resultados Finais
- `baseline_vs_v2_comparison.md` - Comparação baseline × versão final
- `production_readiness_assessment.md` - Avaliação de prontidão para produção

## Como usar

1. Para validar os resultados: compare os logs com os thresholds definidos
2. Para reproduzir: use as configurações em `datasets/` 
3. Para entender correções: veja a evolução de v1 para v2

## Principais Achados

- **V01 (Alta)**: Falha de segurança sob urgência - RT05
- **V02 (Média)**: Fuga de escopo via Browser - RT15  
- **F01 (Alta)**: Alucinação técnica - TC05 Faithfulness 0.71

Gerado em: $(Get-Date -Format 'dd/MM/yyyy HH:mm')