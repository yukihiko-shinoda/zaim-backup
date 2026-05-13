FROM futureys/claude-code-python-development:20260512134000
# COPY pyproject.toml uv.lock /workspace/
COPY pyproject.toml /workspace/
RUN uv sync --python 3.13.12
COPY . /workspace/
