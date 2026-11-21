FROM python:3.12-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
WORKDIR /opt/relay
COPY requirements-runtime.txt .
RUN python -m pip install --no-cache-dir -r requirements-runtime.txt
COPY relay.py release-profile.json ./
ARG RELAY_REVISION=local
ENV RELAY_REVISION=${RELAY_REVISION} PYTHONDONTWRITEBYTECODE=1 PORT=8080
USER 17061:17061
EXPOSE 8080
CMD ["gunicorn", "--workers", "1", "--access-logfile", "-", "relay:create_service()"]
