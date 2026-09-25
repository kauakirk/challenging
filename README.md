# MotoAssist — AgentCore Evaluation

Avaliação do agente **MotoAssist** usando o SDK oficial `bedrock-agentcore`.

## Estrutura

```
motoassist/
├── motoassist_agentcore_dataset.json   # 20 cenários de teste (schema SDK)
└── run_agentcore_eval.py               # Runner de avaliação
```

## Instalação

```bash
pip install bedrock-agentcore boto3
```

## Como executar

```bash
# Credenciais AWS configuradas (aws configure ou variáveis de ambiente)
python motoassist/run_agentcore_eval.py
```

Variáveis de ambiente opcionais:

| Variável | Padrão |
|---|---|
| `AWS_REGION` | `us-east-2` |
| `AGENTCORE_AGENT_ARN` | ARN do MotoAssist |
| `EVALUATION_DELAY` | `180` (segundos) |

Os resultados são salvos em `results/agentcore_eval_results.json`.

## Avaliadores

| Avaliador | O que mede |
|---|---|
| `Builtin.Correctness` | Resposta correta vs `expected_response` |
| `Builtin.GoalSuccessRate` | `assertions` satisfeitas por cenário |
| `Builtin.Harmfulness` | Conteúdo prejudicial / segurança |
| `Builtin.InstructionFollowing` | Aderência às instruções do sistema |
| `Builtin.Helpfulness` | Utilidade geral da resposta |

## Dataset

20 cenários em 5 categorias:

| Categoria | Cenários |
|---|---|
| `consulta_direta` | TC01 – TC04 |
| `tarefa_com_ferramenta` | TC05 – TC08 |
| `multi_turno` | TC09 – TC12 |
| `fora_de_escopo` | TC13 – TC15 |
| `adversarial` | TC16 – TC20 |
