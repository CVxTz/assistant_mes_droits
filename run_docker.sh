# Build the Docker image
docker build -t app:latest .

# Run the Docker container
docker run -p 8080:8080 --env-file .env app:latest