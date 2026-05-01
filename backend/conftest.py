"""Configuration globale pytest : env vars de test + sys.path."""
import os
import sys

# S'assurer que le dossier backend/ est dans sys.path pour les imports
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Variables d'environnement de test : on desactive Jaeger/Logstash
os.environ.setdefault("JAEGER_ENDPOINT", "")
os.environ.setdefault("LOGSTASH_HOST", "127.0.0.1")
os.environ.setdefault("LOGSTASH_PORT", "9999")
os.environ.setdefault("JWT_SECRET", "test-secret-32-chars-minimum-please")
os.environ.setdefault("DISABLE_TRACING", "true")
