FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV CONFIG_PATH=/etc/stemweek/user-config.ini

EXPOSE 8001

ENTRYPOINT ["python", "main.py"]
