# Velocimeter Finance HTTP API 🚲💨🕸️

Velocimeter Finance HTTP API is used by our app to fetch tokens and liquidity
pool pairs.

Please make sure you have [Docker](https://docs.docker.com/install/) first.

To build the image, run:

```
$ docker build ./ -t velodrome/api
```

Next, populate the `env.example.base` file, and update the relevant variables.

Finally, to start the container, run:

```
$ docker run --rm --env-file=env.example.base -v $(pwd):/app -p 3001:3001 -w /app -it velodrome/api
```

To run the syncer (refreshes data from chain) process, run:

```
$ docker run --rm --env-file=env.example.base -v $(pwd):/app -p 3001:3001 -w /app -it velodrome/api sh -c 'python -m app.pairs.syncer'
```
