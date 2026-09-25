"""
set_creds.py
------------
Cole as 3 linhas "export ..." do CloudShell quando solicitado.
O script extrai os valores e grava em ~/.aws/credentials como perfil [sso].

Uso:
    python set_creds.py

Depois rode os scripts com:
    set AWS_PROFILE=sso && python motoassist/test_invoke.py
"""

import re
import os
import configparser
from pathlib import Path

print("Cole as linhas 'export ...' do CloudShell e pressione Enter duas vezes:\n")

lines = []
while True:
    line = input()
    if line.strip() == "":
        break
    lines.append(line.strip())

text = "\n".join(lines)

key    = re.search(r'AWS_ACCESS_KEY_ID=(\S+)', text)
secret = re.search(r'AWS_SECRET_ACCESS_KEY=(\S+)', text)
token  = re.search(r'AWS_SESSION_TOKEN=(\S+)', text)

if not all([key, secret, token]):
    print("Não encontrei as 3 variáveis. Tente novamente.")
    exit(1)

key_val    = key.group(1)
secret_val = secret.group(1)
token_val  = token.group(1)

# Grava no arquivo ~/.aws/credentials
creds_path = Path.home() / ".aws" / "credentials"
creds_path.parent.mkdir(exist_ok=True)

config = configparser.ConfigParser()
if creds_path.exists():
    config.read(creds_path)

config["sso"] = {
    "aws_access_key_id":     key_val,
    "aws_secret_access_key": secret_val,
    "aws_session_token":     token_val,
    "region":                "us-east-2",
}

with open(creds_path, "w") as f:
    config.write(f)

print(f"\nCredenciais salvas em {creds_path} como perfil [sso]")
print("\nAgora rode:")
print('  $env:AWS_PROFILE = "sso"')
print("  python motoassist/test_invoke.py")

# Verifica
import boto3
try:
    session = boto3.Session(profile_name="sso")
    arn = session.client("sts", region_name="us-east-2").get_caller_identity()["Arn"]
    print(f"\nOK — identidade: {arn}")
except Exception as e:
    print(f"\nErro na verificação: {e}")
