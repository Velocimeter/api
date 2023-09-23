FROM pypy:3.9-slim-bullseye

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc g++ libssl-dev libev-dev
RUN apt-get clean

WORKDIR /app
COPY ./ /app

RUN pip install -e . --no-binary :all: --no-cache-dir

EXPOSE 3000

CMD ["python", "-m", "app.app"]
