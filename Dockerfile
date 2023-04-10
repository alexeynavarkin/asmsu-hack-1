FROM python:3.11

WORKDIR /app

COPY . .

ENTRYPOINT [ "python", "main.py" ]