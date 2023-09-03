FROM python:latest

WORKDIR /app

# Install the PostgreSQL client tools
# RUN add-apt-repository main
# RUN add-apt-repository universe
RUN apt-get update && apt-get install -y lsb-release
RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list &&\
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update && apt-get install -y postgresql-client-9.6 postgresql-client-14

RUN mkdir -p backups &&\
    mkdir -p data

COPY requirements.txt .
COPY migrate.py .
RUN  python3 -m pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "migrate.py" ]