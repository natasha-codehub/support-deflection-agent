import os

CONFIDENCE_HIGH = float(os.getenv("CONFIDENCE_HIGH", "0.80"))
CONFIDENCE_MEDIUM = float(os.getenv("CONFIDENCE_MEDIUM", "0.65"))
MAX_ESCALATION_RATE_TARGET = 0.25
SESSION_MEMORY_TURNS = 6
RAG_TOP_K = 5
RAG_SCORING_WINDOW = 3

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ORG_NAME = os.getenv("ORG_NAME", "AcmeCo Industrial")
ORG_DOMAIN = os.getenv("ORG_DOMAIN", "B2B industrial gas distribution")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
KB_PATH = os.path.join(os.path.dirname(__file__), "kb")
MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), "mock_data")

EMBEDDING_MODEL = "models/text-embedding-004"
GEMINI_MODEL = "gemini-2.0-flash"
