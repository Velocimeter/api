FROM pypy:3.9-slim-bullseye

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc libssl-dev libev-dev
RUN apt-get clean

WORKDIR /app
COPY ./ /app

RUN python app/setup.py install

EXPOSE 3000

CMD ["python", "./app/app.py"]
