"""
conftest.py — configuração global do pytest para DeepEval
"""
import os
from dotenv import load_dotenv

# Carrega variáveis do .env na raiz do projeto
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
