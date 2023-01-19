FROM pypy:3.9-slim-bullseye@sha256:79fe86e4efc8c9376bfad87efc366d9f241d5dd3e0d3238bbd61d8edf2564b1a

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc g++ libssl-dev libev-dev
RUN apt-get clean

WORKDIR /app
COPY ./ /app

RUN pip install -e .

EXPOSE 3000

CMD ["python", "-m", "app.app"]
