FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8800

# --proxy-headers + --forwarded-allow-ips '*' makes uvicorn trust X-Forwarded-For
# from Caddy/NPM. Without this, request.client.host is the docker peer IP (e.g.
# 172.18.0.4) and the spam-defense IP capture is junk. The API container must
# never be exposed directly — Caddy/NPM is always the only ingress.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8800", \
     "--proxy-headers", "--forwarded-allow-ips", "*"]
