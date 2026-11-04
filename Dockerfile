FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /bin/uv
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY api_tests ./api_tests
COPY tests ./tests

RUN useradd --system --uid 10001 tester
USER tester
ENV PATH="/app/.venv/bin:$PATH" \
    PYTEST_ADDOPTS="-p no:cacheprovider"

ENTRYPOINT ["pytest"]
CMD ["-v"]
