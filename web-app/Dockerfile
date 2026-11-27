FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv sync --system

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]