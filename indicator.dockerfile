FROM python:3.12-bookworm

RUN mkdir -p /app/dashboard
WORKDIR /app/dashboard

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ../

RUN pip install --no-cache-dir -r ../requirements.txt

RUN git clone https://github.com/fbardos/odapi-dashboard.git .

EXPOSE 8501

ENTRYPOINT ["conda", "run", "--live-stream", "-n", "odapi_dashboard", "streamlit", "run", "apps/app_indikator.py", "--server.port=8501", "--server.address=0.0.0.0"]
