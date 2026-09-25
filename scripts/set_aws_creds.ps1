# set_aws_creds.ps1
# ------------------
# Cole aqui as credenciais temporárias do CloudShell e rode:
#   . .\set_aws_creds.ps1   (com o ponto na frente para aplicar na sessão atual)
#
# Para renovar: rode "aws configure export-credentials --format env" no CloudShell
# e atualize os valores abaixo.

$env:AWS_ACCESS_KEY_ID     = "COLE_AQUI"
$env:AWS_SECRET_ACCESS_KEY = "COLE_AQUI"
$env:AWS_SESSION_TOKEN     = "COLE_AQUI"
$env:AWS_DEFAULT_REGION    = "us-east-2"

# Confirma identidade
python -c "import boto3; r = boto3.client('sts').get_caller_identity(); print('OK -', r['Arn'])"
