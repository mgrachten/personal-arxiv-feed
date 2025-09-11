# Arxiv Personal Feed

A personal Arxiv feed server that filters papers based on your interests.

## Description

This project is a FastAPI application that provides a personalized feed of Arxiv papers. It fetches the latest papers from specified categories daily, uses an LLM to classify them based on your interests, and displays the relevant ones on a simple web interface.

## Features

-   **Personalized Feed**: Filters Arxiv papers based on your defined interests.
-   **Automatic Classification**: Uses an LLM to classify papers as relevant or not.
-   **Web Interface**: A simple web interface to view the feed and manage your interests.
-   **Scheduled Updates**: Automatically fetches and classifies new papers daily.

## Configuration

All configuration is done in the `src/arxiv_personal_feed/config.py` file. You can modify the following settings:

-   **LLM Settings**:
    -   `llm_model`: The model to use for classification (e.g., `"google-gla:gemini-2.5-flash-lite"`, or `"openai:gpt-4.1-nano"`).
    -   `llm_batch_size`: The number of articles to classify in a single batch.
    -   `llm_fields_to_include`: The fields of the article to use for classification (e.g., `["title", "abstract"]`).
-   **Scheduler Settings**:
    -   `scheduler_timezone`: The timezone for the daily update (e.g., `"US/Eastern"`).
    -   `scheduler_hour`: The hour of the day to run the daily update (0-23).
    -   `scheduler_minute`: The minute of the hour to run the daily update (0-59).
-   **Server Settings**:
    -   `server_port`: The port to run the server on (e.g., `8000`).
-   **Arxiv Settings**:
    -   `arxiv_max_results_per_category`: The maximum number of new articles to fetch from each Arxiv category during an update.

## Getting Started

### Prerequisites

-   Python 3.10+
-   An Gemini/OpenAI API key (or other compatible API key for classification)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/arxiv-personal-feed.git
    cd arxiv-personal-feed
    ```

2.  **Install dependencies:**

    It is recommended to use a virtual environment.

    Using `venv` and `pip`:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```

    Alternatively, using `uv`:
    ```bash
    uv venv
    uv pip install -e .
    ```

3.  **Set up your API key:**

    You will need to set your API key as an environment variable. For example:

    ```bash
    export OPENAI_API_KEY="your-api-key"
    ```

### Running the Application

To start the server, run the following command:

```bash
arxiv-personal-feed
```

Alternatively, when using `uv`:

```bash
uv run arxiv-personal-feed
```

The application will be available at `http://localhost:8000`.

## Usage

1.  **Define your interests**:
    -   Navigate to `http://localhost:8000/interests`.
    -   Add the Arxiv categories you are interested in (e.g., `cs.AI`, `cs.SD`).
    -   Add your specific interests, one per line (e.g., `Large Language Models`, `Reinforcement Learning`).
    -   Click "Update".

2.  **View your feed**:
    -   Navigate to `http://localhost:8000`.
    -   The feed will be populated with relevant papers. This may take a few minutes after you have updated your interests.
    -   The feed will be automatically updated daily.
