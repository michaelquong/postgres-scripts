FROM python:latest

WORKDIR /app

# Install the PostgreSQL client tools
RUN apt-get update && apt-get install -y postgresql-client

COPY . /app
RUN make requirements

ENTRYPOINT [ "python" ]
CMD [ "main.py" ]