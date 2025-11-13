"""
Configuration file for Category Mapper
Copy this to config.py and update with your settings
"""

# File Paths
INPUT_FILE = r"C:\path\to\your\Category_mapping_template.xlsx"
# OUTPUT_FILE will be auto-generated as: {INPUT_FILE}_Tesco.xlsx
# AUTOSAVE_FILE will be auto-generated as: {INPUT_FILE}_Tesco_Mapped_autosave.xlsx
# LOG_FILE will be saved in same directory as INPUT_FILE

# API Configuration
API_URL = "https://your-ngrok-url.ngrok-free.dev/generate"

# Processing Parameters
TOP_N_MATCHES = 30  # Number of candidates to send to LLM
MAX_CONCURRENT_REQUESTS = 2  # Concurrent API calls (adjust based on API limits)
SIMILARITY_THRESHOLD = 0.85  # Minimum similarity score for auto-accept (0.0 to 1.0)
AUTOSAVE_INTERVAL = 10  # Save progress every N items

# Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence transformer model for embeddings

# Matching Configuration
MAX_TRAILING_DEPTH = 3  # Maximum depth for trailing segment matching

# Logging
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
