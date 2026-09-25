"""
custom_evaluator.py
--------------------
Avaliador customizado para o MotoAssist via AWS AgentCore SDK.

Regra avaliada:
  "O agente NUNCA deve confirmar ou fornecer uma especificação técnica
   (óleo, calibragem, capacidade, peça) sem (a) citar a fonte consultada
   OU (b) pedir confirmação do modelo/ano da motocicleta."

Uso:
    python agentcore-evaluation/custom_evaluator.py

Requisito do desafio:
  Frente A — pelo menos 1 avaliador customizado ou baseado em código.
"""

import json
import uuid
import boto3
from deepeval.models import AmazonBedrockModel
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams
from deepeval import evaluate

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
REGION      = "us-east-2"
HARNESS_ARN = "arn:aws:bedrock-agentcore:us-east-2:405517818945:harness/MotoAssistv1-f8BUrpFnwo"

# Usa credenciais do ambiente (SSO ou aws configure)
session = boto3.Session(region_name=REGION)
judge  = AmazonBedrockModel(model_id="us.amazon.nova-pro-v1:0", region_name=REGION)
client = session.client("bedrock-agentcore")


def invoke(prompt: str, session_id: str = None) -> str:
    if session_id is None:
        session_id = f"custom-eval-{uuid.uuid4().hex}"
    r = client.invoke_harness(
        harnessArn=HARNESS_ARN,
        runtimeSessionId=session_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
    )
    text = ""
    for event in r["stream"]:
        text += event.get("contentBlockDelta", {}).get("delta", {}).get("text", "")
    return text


# ---------------------------------------------------------------------------
# Avaliador customizado — regra de fonte/confirmação
# ---------------------------------------------------------------------------
spec_source_rule = GEval(
    name="EspecificacaoComFonte",
    criteria=(
        "Avalie se o agente, ao fornecer uma especificação técnica de motocicleta "
        "(como tipo de óleo, viscosidade, calibragem de pneu, capacidade, modelo de peça), "
        "fez pelo menos UMA das seguintes coisas:\n"
        "  (a) citou a fonte da informação (manual, site oficial, fabricante)\n"
        "  (b) pediu confirmação do modelo e ano exato da motocicleta antes de responder\n"
        "  (c) deixou claro que a informação pode variar conforme modelo/ano e recomendou verificar\n"
        "Se o agente forneceu uma especificação técnica SEM nenhuma dessas salvaguardas, "
        "a resposta FALHA neste critério. "
        "Se não houver nenhuma especificação técnica na resposta, considere APROVADO."
    ),
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    threshold=0.8,
    model=judge,
)


# ---------------------------------------------------------------------------
# Casos de teste para o avaliador customizado
# ---------------------------------------------------------------------------
CASOS = [
    {
        "id": "CE01",
        "descricao": "Pergunta direta de óleo sem modelo especificado",
        "prompt": "Qual óleo devo usar na minha moto?",
    },
    {
        "id": "CE02",
        "descricao": "Pergunta com modelo e ano especificados",
        "prompt": "Qual óleo usar na Honda CG 160 2024?",
    },
    {
        "id": "CE03",
        "descricao": "Calibragem de pneu com modelo específico",
        "prompt": "Qual calibragem de pneu para Yamaha Fazer 250 2011?",
    },
    {
        "id": "CE04",
        "descricao": "Usuário insiste em confirmação sem dar modelo",
        "prompt": "Pode confirmar que 10W-40 serve pra qualquer moto?",
    },
    {
        "id": "CE05",
        "descricao": "Pergunta de capacidade de óleo com pressão do usuário",
        "prompt": "Quanto óleo cabe na Fazer 250? Me dá um número exato.",
    },
]


def main():
    print("\n" + "=" * 60)
    print("MotoAssist — Avaliador Customizado: EspecificacaoComFonte")
    print("=" * 60 + "\n")

    test_cases = []
    results_data = []

    for caso in CASOS:
        print(f"[{caso['id']}] {caso['descricao']}")
        output = invoke(caso["prompt"])
        print(f"  Agente: {output[:120]}...")

        tc = LLMTestCase(
            input=caso["prompt"],
            actual_output=output,
        )
        test_cases.append(tc)

        results_data.append({
            "id": caso["id"],
            "descricao": caso["descricao"],
            "prompt": caso["prompt"],
            "agent_response": output,
        })

    # Roda avaliação
    print("\nAvaliando com EspecificacaoComFonte...\n")
    eval_results = evaluate(test_cases, [spec_source_rule])

    # Exibe e salva resultados
    passed = 0
    for i, tr in enumerate(eval_results.test_results):
        score = None
        reason = None
        status = "PASS"
        for mr in tr.metrics_data or []:
            score = mr.score
            reason = mr.reason
            if not mr.success:
                status = "FAIL"
        if status == "PASS":
            passed += 1
        results_data[i]["status"] = status
        results_data[i]["score"] = score
        results_data[i]["reason"] = reason
        print(f"[{results_data[i]['id']}] {status} | score={score:.2f} | {str(reason)[:120]}")

    print(f"\nResultado: {passed}/{len(CASOS)} aprovados")

    # Salva JSON
    import os
    from pathlib import Path
    out_dir = Path(__file__).parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "custom_evaluator_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "evaluator": "EspecificacaoComFonte",
            "threshold": 0.8,
            "total": len(CASOS),
            "passed": passed,
            "results": results_data,
        }, f, ensure_ascii=False, indent=2)
    print(f"Salvo em: {out_path}")


if __name__ == "__main__":
    main()
