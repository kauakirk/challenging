"""
run_agentcore_eval.py
---------------------
Avaliação do agente MotoAssist usando o SDK oficial bedrock-agentcore.

Fluxo:
  1. Carrega motoassist_agentcore_dataset.json via FileDatasetProvider
  2. OnDemandEvaluationDatasetRunner invoca o agente para cada cenário,
     aguarda ingestão do CloudWatch e executa os avaliadores automaticamente
  3. Resultados salvos em ../results/agentcore_eval_results.json

Instalação:
  pip install bedrock-agentcore boto3

Variáveis de ambiente (opcionais, sobrescrevem as constantes abaixo):
  AWS_REGION          — região AWS           (padrão: us-east-2)
  AGENTCORE_AGENT_ARN — ARN do runtime       (padrão: valor abaixo)
  EVALUATION_DELAY    — segundos de espera   (padrão: 180)
"""

import json
import os
from pathlib import Path

import boto3
from bedrock_agentcore.evaluation import (
    AgentInvokerInput,
    AgentInvokerOutput,
    CloudWatchAgentSpanCollector,
    EvaluationRunConfig,
    EvaluatorConfig,
    FileDatasetProvider,
    OnDemandEvaluationDatasetRunner,
)

# ---------------------------------------------------------------------------
# Configuração — edite aqui ou use variáveis de ambiente
# ---------------------------------------------------------------------------
REGION = os.getenv("AWS_REGION", "us-east-2")

AGENT_ARN = os.getenv(
    "AGENTCORE_AGENT_ARN",
    "arn:aws:bedrock-agentcore:us-east-2:405517818945:runtime/harness_MotoAssistv1-yjxjcECuE8",
)

# Log group gerado automaticamente pelo AgentCore: /aws/bedrock-agentcore/runtimes/<agent-id>-DEFAULT
_agent_id = AGENT_ARN.split("/")[-1]
LOG_GROUP = f"/aws/bedrock-agentcore/runtimes/{_agent_id}-DEFAULT"

EVALUATION_DELAY = int(os.getenv("EVALUATION_DELAY", "180"))

DATASET_PATH = Path(__file__).parent / "motoassist_agentcore_dataset.json"
RESULTS_DIR  = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)
RESULTS_PATH = RESULTS_DIR / "agentcore_eval_results.json"

# ---------------------------------------------------------------------------
# Cliente AgentCore
# ---------------------------------------------------------------------------
agentcore_client = boto3.client("bedrock-agentcore", region_name=REGION)


# ---------------------------------------------------------------------------
# Agent invoker — chamado pelo runner para cada turno
# ---------------------------------------------------------------------------
def agent_invoker(invoker_input: AgentInvokerInput) -> AgentInvokerOutput:
    """Envia um turno ao MotoAssist e retorna a resposta."""
    payload = invoker_input.payload

    # Normaliza o payload para bytes JSON
    if isinstance(payload, str):
        payload = json.dumps({"prompt": payload}).encode()
    elif isinstance(payload, dict):
        payload = json.dumps(payload).encode()

    print(f"  [{invoker_input.session_id}] >> {payload.decode()[:120]}")

    response = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_ARN,
        runtimeSessionId=invoker_input.session_id,
        payload=payload,
    )

    response_body = response["response"].read()
    print(f"  [{invoker_input.session_id}] << {response_body.decode()[:120]}")

    return AgentInvokerOutput(agent_output=json.loads(response_body))


# ---------------------------------------------------------------------------
# Execução principal
# ---------------------------------------------------------------------------
def main():
    print(f"\n{'='*60}")
    print("MotoAssist — AgentCore Evaluation")
    print(f"  Region   : {REGION}")
    print(f"  Agent ARN: {AGENT_ARN}")
    print(f"  Dataset  : {DATASET_PATH}")
    print(f"  Results  : {RESULTS_PATH}")
    print(f"{'='*60}\n")

    # 1. Carrega o dataset
    dataset = FileDatasetProvider(str(DATASET_PATH)).get_dataset()
    print(f"Cenários carregados: {len(dataset.scenarios)}\n")

    # 2. Span collector — lê telemetria do CloudWatch
    span_collector = CloudWatchAgentSpanCollector(
        log_group_name=LOG_GROUP,
        region=REGION,
    )

    # 3. Configuração dos avaliadores
    config = EvaluationRunConfig(
        evaluator_config=EvaluatorConfig(
            evaluator_ids=[
                "Builtin.Correctness",           # resposta correta vs expected_response
                "Builtin.GoalSuccessRate",        # assertions satisfeitas
                "Builtin.Harmfulness",            # conteúdo prejudicial / segurança
                "Builtin.InstructionFollowing",   # segue instruções do sistema
                "Builtin.Helpfulness",            # utilidade geral da resposta
            ],
        ),
        evaluation_delay_seconds=EVALUATION_DELAY,
        max_concurrent_scenarios=5,
    )

    # 4. Executa
    runner = OnDemandEvaluationDatasetRunner(region=REGION)
    result = runner.run(
        agent_invoker=agent_invoker,
        dataset=dataset,
        span_collector=span_collector,
        config=config,
    )

    # 5. Imprime resumo
    print(f"\n{'='*60}")
    print(f"Concluído: {len(result.scenario_results)} cenário(s)\n")

    passed = 0
    for scenario in result.scenario_results:
        status_icon = "✓" if scenario.status == "COMPLETED" else "✗"
        print(f"[{status_icon}] {scenario.scenario_id} — {scenario.status}")

        if scenario.error:
            print(f"    Erro: {scenario.error}")
            continue

        for ev in scenario.evaluator_results:
            for r in ev.results:
                score = r.get("value", "—")
                label = r.get("label", "—")
                expl  = r.get("explanation", "")[:120]
                print(f"    {ev.evaluator_id}: score={score} label={label}")
                if expl:
                    print(f"      → {expl}")

        if scenario.status == "COMPLETED":
            passed += 1

    total = len(result.scenario_results)
    print(f"\nPass rate: {passed}/{total} ({round(passed/total*100, 1) if total else 0}%)")
    print(f"{'='*60}\n")

    # 6. Salva resultados completos em JSON
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(indent=2))

    print(f"Resultados salvos em: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
