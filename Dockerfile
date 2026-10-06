FROM futureys/claude-code-python-development:20261002121500
COPY pyproject.toml uv.lock /workspace/
RUN uv sync
COPY . /workspace/
