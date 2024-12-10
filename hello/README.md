# How to run

Go to the directory with the dockerfile (`hello/`).

## Build the image (once pip requirements change)
```bash
docker build -t aasd .
```

## Run the container
```bash
docker run -it -v src:/app/src aasd
```