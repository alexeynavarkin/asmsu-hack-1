FROM python:3.10

WORKDIR /app

COPY . .

ENTRYPOINT [ "python", "main.py" ]