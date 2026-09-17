FROM futureys/claude-code-python-development:20260913152000
COPY pyproject.toml uv.lock /workspace/
RUN uv sync
COPY . /workspace/
