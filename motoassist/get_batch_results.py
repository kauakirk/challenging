"""
get_batch_results.py
--------------------
Busca os resultados da avaliação em lote já criada no console AWS AgentCore.
Não precisa invocar o agente — apenas faz polling do job existente.

Uso:
    python motoassist/get_batch_results.py

Salva resultado em:
    results/agentcore_batch_results.json
"""

import json
import time
from pathlib import Path
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
REGION = "us-east-2"

# ARN da avaliação em lote criada no console
BATCH_EVAL_ARN = "arn:aws:bedrock-agentcore:us-east-2:405517818945:batch-evaluate/motoassist_agentcore_baseline-da414df0d7"

# Extrai o ID do ARN (parte após o último /)
BATCH_EVAL_ID = BATCH_EVAL_ARN.split("/")[-1]

RESULTS_DIR  = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)
RESULTS_PATH = RESULTS_DIR / "agentcore_batch_results.json"

POLL_INTERVAL = 15   # segundos entre cada polling
POLL_TIMEOUT  = 1800 # máximo 30 min esperando

# ---------------------------------------------------------------------------
# Cliente
# ---------------------------------------------------------------------------
client = boto3.client("bedrock-agentcore", region_name=REGION)


# ---------------------------------------------------------------------------
# Polling
# ---------------------------------------------------------------------------
def get_batch_evaluation(eval_id: str) -> dict:
    response = client.get_batch_evaluation(batchEvaluationId=eval_id)
    return response


def poll_until_complete(eval_id: str) -> dict:
    terminal_states = {"COMPLETED", "FAILED", "STOPPED"}
    elapsed = 0

    print(f"\nPolling avaliação: {eval_id}")
    print(f"{'='*60}")

    while elapsed < POLL_TIMEOUT:
        try:
            result = get_batch_evaluation(eval_id)
        except ClientError as e:
            print(f"Erro ao consultar: {e}")
            raise

        status = result.get("status", "UNKNOWN")
        print(f"[{elapsed:>4}s] Status: {status}")

        if status in terminal_states:
            return result

        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    raise TimeoutError(f"Avaliação não concluiu em {POLL_TIMEOUT}s")


# ---------------------------------------------------------------------------
# Exibe resultados
# ---------------------------------------------------------------------------
def print_results(result: dict):
    status = result.get("status")
    name   = result.get("batchEvaluationName", "—")
    created = result.get("createdAt", "—")

    print(f"\n{'='*60}")
    print(f"Nome    : {name}")
    print(f"Status  : {status}")
    print(f"Criado  : {created}")

    eval_results = result.get("evaluationResults", {})
    if not eval_results:
        print("\nSem resultados de avaliação ainda.")
        return

    print(f"\nSessões:")
    print(f"  Concluídas : {eval_results.get('numberOfSessionsCompleted', '—')}")
    print(f"  Em progresso: {eval_results.get('numberOfSessionsInProgress', '—')}")
    print(f"  Falhas     : {eval_results.get('numberOfSessionsFailed', '—')}")
    print(f"  Total      : {eval_results.get('totalNumberOfSessions', '—')}")

    summaries = eval_results.get("evaluatorSummaries", [])
    if summaries:
        print(f"\nResultados por avaliador:")
        for s in summaries:
            evaluator_id = s.get("evaluatorId", "—")
            stats        = s.get("statistics", {})
            avg_score    = stats.get("averageScore", "—")
            total_eval   = s.get("totalEvaluated", "—")
            total_failed = s.get("totalFailed", 0)
            print(f"  {evaluator_id}")
            print(f"    Score médio : {avg_score}")
            print(f"    Avaliados   : {total_eval}")
            print(f"    Falhas      : {total_failed}")

    errors = result.get("errorDetails", [])
    if errors:
        print(f"\nErros:")
        for e in errors:
            print(f"  - {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"Buscando resultados da avaliação em lote...")
    print(f"ARN: {BATCH_EVAL_ARN}")

    # Tenta buscar primeiro sem polling (pode já estar concluída)
    try:
        result = get_batch_evaluation(BATCH_EVAL_ID)
        status = result.get("status", "UNKNOWN")

        if status not in {"COMPLETED", "FAILED", "STOPPED"}:
            # Ainda em andamento — faz polling
            result = poll_until_complete(BATCH_EVAL_ID)
        else:
            print(f"\nAvaliação já concluída com status: {status}")

    except ClientError as e:
        print(f"\nErro: {e}")
        raise

    # Imprime resumo
    print_results(result)

    # Salva JSON completo
    # Converte datetime para string para serialização
    def default_serializer(obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return str(obj)

    output = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "batch_evaluation_arn": BATCH_EVAL_ARN,
        "raw_response": result,
    }

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=default_serializer)

    print(f"\n{'='*60}")
    print(f"Resultados salvos em: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
