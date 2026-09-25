#!/bin/bash
# run_all_v3.sh — Executa toda a avaliação pós-prompt v3 no CloudShell
#
# Uso:
#   cd /tmp/challenging
#   bash scripts/run_all_v3.sh
#
# Requer: pip install bedrock-agentcore deepeval boto3 aiobotocore

set -e
echo "======================================"
echo " MotoAssist — Avaliação Pós-Prompt v3"
echo "======================================"
echo ""

# 1. Frente A — Avaliação direta AgentCore
echo "[1/4] AgentCore Evaluations (direct eval v3)..."
python3 agentcore-evaluation/run_direct_eval.py _v3
echo ""

# 2. Avaliador customizado
echo "[2/4] Avaliador customizado EspecificacaoComFonte..."
python3 agentcore-evaluation/custom_evaluator.py
echo ""

# 3. DeepEval
echo "[3/4] DeepEval Frente B..."
python3 -m pytest deepeval/test_motoassist.py -v 2>&1 | tee results/deepeval_v3_output.txt
echo ""

# 4. Red teaming
echo "[4/4] Red Teaming v3..."
python3 red-team/run_red_team.py _v3
echo ""

echo "======================================"
echo " Concluido. Resultados em results/"
echo "======================================"

git add results/
git commit -m "results: v3 evaluation results (post-prompt update)" 2>/dev/null && \
  git push origin main 2>/dev/null || \
  echo "Git push falhou — rode manualmente: git push origin main"
