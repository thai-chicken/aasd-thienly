# How to run

Go to the directory with the dockerfile (`hello/`).

## Build the image (once pip requirements change)
```bash
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
