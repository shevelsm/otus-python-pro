FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=on

COPY requirements.txt /
RUN pip install --no-cache-dir -q -r requirements.txt

WORKDIR /app
COPY . .

EXPOSE 8080
CMD ["python", "api.py"]