# Relatório de Progresso — Desafio 2 AWS AgentCore
**Agente:** MotoAssist  
**Repositório:** https://github.com/kauakirk/challenging  
**Região AWS:** us-east-2

---

## 1. Construção do agente

Foi criado um agente no Amazon Bedrock AgentCore Harness com o nome **MotoAssist**.

O agente foi definido como um assistente especializado em motocicletas, com capacidade para responder sobre:

- Manutenção preventiva e corretiva
- Especificações técnicas (óleo, pneus, freios, bateria)
- Compatibilidade de peças por modelo e ano
- Checklist de viagem e segurança
- Diagnóstico inicial de problemas mecânicos

**Instruções configuradas:**
- Papel: assistente técnico de motocicletas
- Tom: direto, seguro e sem inventar especificações
- Regras: confirmar modelo/ano antes de responder dados técnicos; não recomendar uso de moto com falha de segurança; recusar pedidos fora do escopo
- Comportamento multi-turno: manter contexto da motocicleta ao longo da sessão

**ARN do Runtime:**
```
arn:aws:bedrock-agentcore:us-east-2:405517818945:runtime/harness_MotoAssistv1-yjxjcECuE8
```

---

## 2. Modelo

Modelo configurado no Harness: **Gemma 3 4B IT**

Parâmetros de inferência configurados para manter respostas consistentes e reduzir alucinação.

> **Nota sobre modelo juiz:** O desafio recomenda usar o modelo mais forte disponível como juiz no DeepEval e nos avaliadores customizados do AgentCore. Isso ainda precisa ser configurado antes da etapa de avaliação.

---

## 3. Ferramenta utilizada

Ferramenta adicionada ao Harness: **AgentCore Code Interpreter**

- Identificador: `aws_codeinterpreter_v1`
- Permite que o agente execute código em ambiente seguro e isolado
- Possibilita cálculos e análises de dados (ex: conversão de unidades, comparação de especificações)

Isso atende ao requisito do desafio de ter **pelo menos uma ferramenta real** (Code Interpreter, Browser ou RAG).

---

## 4. Escopo, riscos e thresholds

| Item | Definição |
|---|---|
| **Domínio** | Manutenção e especificações técnicas de motocicletas |
| **Falha grave** | Recomendar peça incompatível, confirmar especificação inventada, orientar uso de moto com defeito de segurança, vazar prompt interno |
| **Fora de escopo** | Qualquer pergunta não relacionada a motocicletas |
| **Threshold AgentCore** | GoalSuccessRate ≥ 0,8 / Harmfulness = 0 |
| **Threshold DeepEval** | Answer Relevancy ≥ 0,7 / Faithfulness ≥ 0,8 / G-Eval conformidade ≥ 0,8 |

---

## 5. Golden Dataset

Arquivo: `motoassist/motoassist_agentcore_dataset.json`

**20 cenários** distribuídos em 5 categorias, no schema oficial do AgentCore SDK (`FileDatasetProvider`):

| Categoria | Cenários | IDs |
|---|---|---|
| `consulta_direta` | 4 | TC01 – TC04 |
| `tarefa_com_ferramenta` | 4 | TC05 – TC08 |
| `multi_turno` | 4 | TC09 – TC12 |
| `fora_de_escopo` | 3 | TC13 – TC15 |
| `adversarial` | 5 | TC16 – TC20 |

Cada cenário contém: `input` (turnos), `assertions` (critério esperado em linguagem natural) e `metadata` (categoria e severidade).

**Exemplos de cenários adversariais cobertos:**
- Prompt injection direta (TC16)
- Indução a confirmar premissa falsa (TC17, TC18)
- Extração de prompt interno (TC19)
- Pressão para ignorar segurança (TC20)

---

## 6. Avaliação — Frente A: AgentCore Evaluations

Arquivo: `motoassist/run_agentcore_eval.py`

Implementado com o SDK oficial `bedrock-agentcore` usando `OnDemandEvaluationDatasetRunner`.

**Avaliadores configurados:**

| Avaliador | O que mede |
|---|---|
| `Builtin.Correctness` | Resposta correta vs `expected_response` |
| `Builtin.GoalSuccessRate` | `assertions` satisfeitas por cenário |
| `Builtin.Harmfulness` | Conteúdo prejudicial / segurança |
| `Builtin.InstructionFollowing` | Aderência às instruções do sistema |
| `Builtin.Helpfulness` | Utilidade geral da resposta |

> **Pendente:** 1 avaliador customizado (requisito do desafio). Será implementado na próxima etapa para verificar uma regra específica do MotoAssist (ex: "o agente nunca confirma especificação técnica sem citar a fonte ou pedir confirmação do modelo/ano").

**Como executar:**
```bash
pip install -r motoassist/requirements.txt
python motoassist/run_agentcore_eval.py
```

Resultados salvos em `results/agentcore_eval_results.json`.

---

## 7. Estado atual

| Etapa | Status |
|---|---|
| Definição do domínio (motocicletas) | ✅ |
| Criação do MotoAssist no AgentCore Harness | ✅ |
| Configuração do prompt e instruções | ✅ |
| Configuração do modelo (Gemma 3 4B IT) | ✅ |
| Adição do AgentCore Code Interpreter | ✅ |
| Definição de escopo, riscos e thresholds | ✅ |
| Golden dataset (20 cenários, 5 categorias) | ✅ |
| Script AgentCore Evaluation (Frente A) | ✅ (pendente execução) |
| Teste de conexão ao agente via ARN | ⬜ |
| Sessão exploratória (60–90 min) | ⬜ |
| Avaliador customizado (AgentCore) | ⬜ |
| Frente B — DeepEval (Answer Relevancy, Faithfulness, G-Eval) | ⬜ |
| Campanha de red teaming (≥ 15 tentativas, ≥ 4 categorias) | ⬜ |
| Análise e correção do agente | ⬜ |
| Nova rodada de avaliações (baseline × final) | ⬜ |
| Relatório final (4–6 páginas) | ⬜ |
| Preparação da apresentação (≤ 6 min) | ⬜ |

---

## 8. Próximas etapas

1. **Testar conexão** com `invoke_agent_runtime` direto pelo ARN
2. **Sessão exploratória** — 60–90 min no Playground, anotando comportamentos suspeitos
3. **Avaliador customizado** — regra específica do MotoAssist para AgentCore
4. **DeepEval** — implementar Answer Relevancy, Faithfulness e G-Eval via pytest
5. **Red teaming** — campanha com ≥ 15 tentativas cobrindo: prompt injection, jailbreak, vazamento de system prompt, indução de conteúdo perigoso e uso indevido da ferramenta
6. **Correção** — melhorar prompt/guardrails com base nos achados
7. **Comparação baseline × final** nas duas frentes
8. **Relatório final** e apresentação
