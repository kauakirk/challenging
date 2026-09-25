"""
test_invoke.py
--------------
Teste rápido de conexão com o MotoAssist via invoke_agent_runtime.
Roda um único turno e imprime a resposta — sem avaliação.

Uso:
    pip install boto3
    python motoassist/test_invoke.py
"""

import json
import uuid
import boto3

REGION    = "us-east-2"
AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-2:405517818945:runtime/harness_MotoAssistv1-yjxjcECuE8"

client = boto3.client("bedrock-agentcore", region_name=REGION)

# Gera session_id único para cada teste
session_id = f"test-{uuid.uuid4().hex[:8]}"
prompt     = "Qual óleo devo usar na Honda CG 160 2024?"

print(f"Session ID : {session_id}")
print(f"Prompt     : {prompt}")
print("-" * 50)

response = client.invoke_agent_runtime(
    agentRuntimeArn=AGENT_ARN,
    runtimeSessionId=session_id,
    payload=json.dumps({"prompt": prompt}).encode(),
    qualifier="DEFAULT",
)

body = response["response"].read()
data = json.loads(body)

print("Resposta do agente:")
print(json.dumps(data, ensure_ascii=False, indent=2))
