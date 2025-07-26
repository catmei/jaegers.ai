# ClipHunt Agent

This project is a web application that allows you to generate a video storyboard from a topic. It uses a sophisticated AI agent to research the topic, write a script, and find relevant YouTube clips.

[![Watch a demo of ClipHunt Agent](https://img.youtube.com/vi/1rl1_QeESb8/0.jpg)](https://www.youtube.com/watch?v=1rl1_QeESb8)

## Project Structure

The project is divided into two main parts:

-   `vfront`: A [Next.js](https://nextjs.org/) application that provides the user interface.
-   `backend`: A [Flask](https://flask.palletsprojects.com/) application that exposes the AI agent as a REST API.

## Getting Started

### Prerequisites

-   [Node.js](https://nodejs.org/) (v20 or later)
-   [Python](https://www.python.org/) (v3.9 or later)
-   `pip`
-   `npm` (or `yarn` or `pnpm`)

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file in the `backend` directory and add your API keys:**


5.  **Run the backend server:**
    ```bash
    python api_server.py
    ```
    The backend server will be running at `http://localhost:5001`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd vfront
    ```

2.  **Install the Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Run the frontend development server:**
    ```bash
    npm run dev
    ```
    The frontend application will be running at `http://localhost:3000`.

## Usage

1.  Make sure both the backend and frontend servers are running.
2.  Open your browser and navigate to `http://localhost:3000`.
3.  Enter a topic in the input field and click "Generate Video Plan".
4.  The application will then display a video storyboard with clips from YouTube. 