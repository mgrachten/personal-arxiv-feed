# Arxiv Personal Feed

A personal Arxiv feed server that filters papers based on your interests.

## Description

This project is a FastAPI application that provides a personalized feed of Arxiv papers. It fetches the latest papers from specified categories, uses an LLM to classify them based on your interests, and displays the relevant ones on a simple web interface.

## Features

-   **Personalized Feed**: Filters Arxiv papers based on your defined interests.
-   **Automatic Classification**: Uses an LLM to classify papers as relevant or not.
-   **Web Interface**: A simple web interface to view the feed and manage your interests.
-   **Scheduled Updates**: Automatically fetches and classifies new papers daily.

## Getting Started

### Prerequisites

-   Python 3.10+
-   An OpenAI API key (or other compatible API key for classification)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/arxiv-personal-feed.git
    cd arxiv-personal-feed
    ```

2.  **Install dependencies:**

    It is recommended to use a virtual environment.

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```

3.  **Set up your environment:**

    Create a `.env` file in the project root and add your OpenAI/Gemini API key (depending on the model being used):

    ```
    OPENAI_API_KEY=your-api-key
    GEMINI_API_KEY=your-api-key

    ```

### Running the Application

To start the server, run the following command:

```bash
arxiv-personal-feed
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
