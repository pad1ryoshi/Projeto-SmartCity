FROM prom/node-exporter:latest as builder

FROM python:3.9

WORKDIR /app

COPY --from=builder /bin/node_exporter /bin/node_exporter

RUN apt-get update && apt-get install -y supervisor iproute2 iputils-ping && rm -rf /var/lib/apt/lists/*
RUN pip install paho-mqtt
COPY app.py .
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
EXPOSE 9100

CMD ["/usr/bin/supervisord"]
