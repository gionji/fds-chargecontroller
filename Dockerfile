FROM python:3.8-alpine
RUN pip install --no-cache-dir paho-mqtt pyserial pymodbus smbus2
RUN mkdir -p /app/src
WORKDIR /app/src
COPY app .
CMD ["python", "-m", "sensor"]