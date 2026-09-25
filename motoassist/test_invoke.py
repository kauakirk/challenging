"""
test_invoke.py
--------------
Teste rápido de conexão com o MotoAssist via invoke_harness.
"""

import uuid
import boto3

REGION      = "us-east-2"
HARNESS_ARN = "arn:aws:bedrock-agentcore:us-east-2:405517818945:harness/MotoAssistv1-f8BUrpFnwo"

client     = boto3.client("bedrock-agentcore", region_name=REGION)
session_id = f"test-{uuid.uuid4().hex}"
prompt     = "Qual óleo devo usar na Honda CG 160 2024?"

print(f"Session ID : {session_id}")
print(f"Prompt     : {prompt}")
print("-" * 50)

response = client.invoke_harness(
    harnessArn=HARNESS_ARN,
    runtimeSessionId=session_id,
    messages=[{"role": "user", "content": [{"text": prompt}]}],
)

full_text = ""
for event in response["stream"]:
    delta = event.get("contentBlockDelta", {}).get("delta", {}).get("text", "")
    full_text += delta

print("Resposta do agente:")
print(full_text)
