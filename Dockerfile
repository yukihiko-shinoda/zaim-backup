FROM futureys/claude-code-python-development:20260805201500
COPY pyproject.toml uv.lock /workspace/
RUN uv sync
COPY . /workspace/
