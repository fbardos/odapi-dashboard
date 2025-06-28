FROM continuumio/miniconda3

RUN mkdir -p /app/dashboard
WORKDIR /app/dashboard

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY environment.yml ../

RUN conda env create -f ../environment.yml --solver libmamba

RUN git clone https://github.com/fbardos/odapi-dashboard.git .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["conda", "run", "-n", "odapi_dashboard", "streamlit", "run", "apps/app_indikator.py", "--server.port=8501", "--server.address=0.0.0.0"]
