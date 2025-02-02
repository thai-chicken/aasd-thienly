# How to run

Go to the directory with the dockerfile (`hello/`).

## Environment variables

Create your own `.env` file based on the `.env.example` file.

```bash
cp .env.example .env
```
Insert your OpenAI API keys and other variables.

## Build the images (every time the pip requirements change)
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
