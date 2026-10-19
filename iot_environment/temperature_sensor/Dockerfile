FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY temperature_sensor.py .

EXPOSE 5001

CMD ["python", "temperature_sensor.py"]