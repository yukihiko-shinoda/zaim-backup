FROM futureys/claude-code-python-development:20260916202000
COPY pyproject.toml uv.lock /workspace/
RUN uv sync
COPY . /workspace/
