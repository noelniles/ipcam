FROM python:3.7
RUN mkdir -p /app/config /app/src
WORKDIR /app
RUN pip install pipenv
COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
RUN pipenv install
CMD ["pipenv", "run", "start", "config/docker_config.json"]
