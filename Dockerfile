FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .

RUN python -m pip install \
    --no-cache-dir \
    -r requirements.txt

COPY helpdesk ./helpdesk

COPY frontend ./frontend

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "helpdesk.api:app", \
     "--host", "0.0.0.0", "--port", "8000"]