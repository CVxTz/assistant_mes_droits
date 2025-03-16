# assistant_mes_droits

This repository contains the code for "assistant_mes_droits," an AI-powered chatbot designed to answer user questions about French citizen rights. It leverages a vector store of information from the official French public service website (Service-Public.fr Particuliers) to provide relevant and sourced answers.

## Overview

The chatbot utilizes a Langchain agent with a retrieval-based approach. When a user asks a question, the agent first generates a search query based on the input. This query is then used to search the vector store for relevant documents. The agent then processes the search results using a large language model (specifically Gemini Pro via the `google-genai` library) to generate concise answers, citing the source URLs whenever possible.

The application is built using Python with FastAPI for the backend API and Alpine.js for a simple web-based user interface. It is designed to be deployed on Google Cloud Run.

## Repository Structure

The repository is organized as follows:

-   `assistant_mes_droits/`: Contains the core application logic.
    -   `agent/`: Defines the Langchain agent and its components.
        -   `agent.py`: Main file for building the agent graph.
        -   `clients.py`: Initializes the Google Gemini client and the vector store client.
        -   `mes_droits_agent.py`: Defines the custom agent logic, including search tool integration and response generation.
    -   `alpine_app/`: Contains the FastAPI application and static files for the user interface.
        -   `main.py`: FastAPI application definition and API endpoints.
        -   `static/`: Contains the HTML, CSS, and JavaScript for the frontend.
        -   `__init__.py`: Initialization file.
    -   `logger.py`: Configures the logging for the application.
    -   `__init__.py`: Initialization file.
-   `.env.example`: Example environment variables file.
-   `.secrets.baseline`: Baseline file for `detect-secrets`.
-   `deploy.sh`: Script for deploying the application to Google Cloud Run.
-   `Dockerfile`: Configuration for building the Docker image.
-   `LICENSE`: Contains the MIT license.
-   `Makefile`: Defines common development tasks.
-   `pyproject.toml`: Project configuration for build systems.
-   `requirements-dev.txt`: Development dependencies.
-   `requirements.txt`: Production dependencies.
-   `ruff.toml`: Configuration for the Ruff linter and formatter.
-   `run_alpine.sh`: Script to run the FastAPI application locally (in and out of Docker).
-   `run_docker.sh`: Script to build and run the Docker container locally.
-   `setup.py`: Installation script for the Python package.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/CVxTz/assistant_mes_droits.git](https://github.com/CVxTz/assistant_mes_droits.git)
    cd assistant_mes_droits
    ```

2.  **Install dependencies:**
    You can install the required Python packages using `pip`:
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt # For development dependencies
    ```
    Alternatively, you can use the `Makefile`:
    ```bash
    make install
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the root directory based on the `.env.example` file and set the `GOOGLE_API_KEY`:
    ```
    GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
    ```
    You will need a Google Cloud API key with access to the Gemini Pro model.

4.  **(Optional) Set up Redis for rate limiting:**
    The application uses Redis for rate limiting. Ensure you have a Redis instance running and set the `REDIS_URI` environment variable in your `.env` file. If you don't have Redis set up, rate limiting will not be active.

## Running the Application

You have several options for running the application:

### Locally (without Docker)

1.  Ensure you have all dependencies installed and the `.env` file configured.
2.  Run the FastAPI application using the `run_alpine.sh` script:
    ```bash
    bash run_alpine.sh dev # For development mode with hot reloading
    # or
    bash run_alpine.sh prod # For production mode
    ```
3.  The application will be accessible at `http://localhost:8080`.

### Using Docker

1.  Ensure you have Docker installed on your system.
2.  Build the Docker image:
    ```bash
    bash run_docker.sh
    ```
3.  The application will be running inside the Docker container and accessible at `http://localhost:8080`.

## Deployment to Google Cloud Run

The `deploy.sh` script automates the deployment process to Google Cloud Run. Before running the script, ensure you have the following:

-   Google Cloud CLI (`gcloud`) installed and configured.
-   A Google Cloud Project with the Cloud Run and Artifact Registry APIs enabled.
-   The `GOOGLE_API_KEY` environment variable set (it will be included in the Cloud Run deployment).

To deploy:

1.  Make the `deploy.sh` script executable:
    ```bash
    chmod +x deploy.sh
    ```
2.  Run the script:
    ```bash
    ./deploy.sh
    ```

The script will:

-   Get your Google Cloud Project ID.
-   Define variables for the repository, location, image name, service name, and version.
-   Create a Docker repository in Artifact Registry if it doesn't exist.
-   Build the Docker image and push it to Artifact Registry.
-   Deploy the image to Cloud Run with specified configurations (e.g., memory, CPU, environment variables, unauthenticated access).

After the script completes, the URL of your deployed Cloud Run service will be displayed.

## Development

For development, you can use the following `Makefile` commands:

-   `make install`: Install all dependencies.
-   `make test`: Run the pytest tests (if any are added).
-   `make format`: Format the code using Ruff.
-   `make lint`: Lint the code using Ruff.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
