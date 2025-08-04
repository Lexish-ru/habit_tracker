# Dockerfile
FROM python:3.12

WORKDIR /app

COPY pyproject.toml poetry.lock* requirements.txt* ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi || pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "habits_project.wsgi:application", "--bind", "0.0.0.0:8000"]
