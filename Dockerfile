# Python version matching the local virtual environment (.venv)
FROM python:3.14-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Follow Hugging Face Spaces non-root user pattern (UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# Install PyTorch CPU-only wheel first to avoid CUDA bloat, then install remaining dependencies
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --user torch==2.14.0 --extra-index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --user -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy repository source code with user ownership
COPY --chown=user:user . $HOME/app

# Ensure data/ and data/cache/ directories exist and are writable by user (UID 1000)
RUN mkdir -p $HOME/app/data/cache && \
    chmod -R u+rwx $HOME/app/data

# Configure PYTHONPATH so scripts/ imports work across sibling modules
ENV PYTHONPATH="$HOME/app/scripts:$HOME/app:$PYTHONPATH"

# Build-time embedding model specification (Hugging Face Hub ID)
ARG NYAAYA_EMBED_MODEL
ENV NYAAYA_EMBED_MODEL=${NYAAYA_EMBED_MODEL}

# At BUILD time: download the cross-encoder and the embedding model,
# and build the section-embeddings cache so runtime startup does not recompute.
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')" && \
    if [ -n "$NYAAYA_EMBED_MODEL" ] || [ -d "finetuned_legal_model_v3" ]; then \
        python -c "from search_core import SearchEngine; SearchEngine()"; \
    fi

# Hugging Face Spaces default port
EXPOSE 7860

# Run FastAPI backend via Uvicorn
CMD ["uvicorn", "main:app", "--app-dir", "scripts", "--host", "0.0.0.0", "--port", "7860"]
