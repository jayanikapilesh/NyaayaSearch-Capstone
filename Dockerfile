# Python version matching the local virtual environment (.venv)
FROM python:3.14-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Follow Hugging Face Spaces non-root user pattern (UID 1000)
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# Install PyTorch CPU-only wheel first to avoid CUDA bloat, then install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.14.0 --extra-index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy repository source code
COPY . $HOME/app

# Ensure data/ and data/cache/ directories exist and are owned by user (UID 1000)
RUN mkdir -p $HOME/app/data/cache && \
    chown -R user:user $HOME

# Switch to non-root user
USER user

# Configure PYTHONPATH so scripts/ imports work across sibling modules
ENV PYTHONPATH="$HOME/app/scripts:$HOME/app:${PYTHONPATH:-}"

# Build-time embedding model specification (Hugging Face Hub ID)
ARG NYAAYA_EMBED_MODEL=duladani/nyaaya-legal-embed-v3
ENV NYAAYA_EMBED_MODEL=${NYAAYA_EMBED_MODEL}

# At BUILD time: download the cross-encoder and the embedding model,
# and build the section-embeddings cache so runtime startup does not recompute.
# Use a dummy GROQ_API_KEY for this build step so no real key is required.
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')" && \
    GROQ_API_KEY=dummy_build_key python -c "from search_core import SearchEngine; SearchEngine()"

# Hugging Face Spaces default port
EXPOSE 7860

# Run FastAPI backend via Uvicorn
CMD ["uvicorn", "main:app", "--app-dir", "scripts", "--host", "0.0.0.0", "--port", "7860"]
