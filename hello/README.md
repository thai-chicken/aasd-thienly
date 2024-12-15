# How to run

Go to the directory with the dockerfile (`hello/`).

## Build the images (every time the pip requirements change)
```bash
docker build -t server-hello .
docker build -t aasd .
```

## Run the container
```bash
docker-compose run --rm --service-ports aasd bash
```

## Run the app (inside the container)
```bash
python src/main.py
```
