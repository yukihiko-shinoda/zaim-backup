FROM futureys/claude-code-python-development:20261014012000
COPY pyproject.toml uv.lock /workspace/
RUN uv sync
COPY . /workspace/
