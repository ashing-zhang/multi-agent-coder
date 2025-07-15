FROM python:3.10-slim

WORKDIR /app

# Patch OS packages to latest security versions
RUN apt-get update && apt-get upgrade -y && apt-get clean

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 