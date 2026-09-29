FROM futureys/claude-code-python-development:20260925125500
COPY pyproject.toml uv.lock /workspace/
RUN uv sync
COPY . /workspace/
