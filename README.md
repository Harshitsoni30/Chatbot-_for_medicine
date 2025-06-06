# Chatbot-_for_medicine
## Overview
This project is a chatbot designed to provide expert suggestions on medicines and healthcare advice. The chatbot leverages **Gemini** LLM capabilities along with curated medical references as a knowledge base. The application is built using FastAPI, Phi Data for **Agentic AI**, and **Gemini** for language processing.

## Features
-Provides medicine suggestions, usage guidelines, and general healthcare tips.
-Uses a structured dataset from trusted medical books and pharmaceutical references.
-Built with **FastAPI** for efficient and scalable API handling.
-Integrates Gemini LLM for natural language understanding and response generation.

## Prerequisites
Before you begin, ensure you have met the following requirements:
- Python 3.8 or higher
- pip (Python package installer)
- A compatible operating system (Windows, macOS, or Linux)

## Installation
Follow these steps to set up the project:

### 1. Clone the repository:
Open your terminal and run the following command:

```bash
https://github.com/Harshitsoni30/Chatbot-_for_medicine.git
```

### 2. Navigate to the project directory:

```bash
ChatBot
```

### 3. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
```

Activate the virtual environment:

- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  venv\Scripts\activate
  ```

### 4. Install the required packages:
Use pip to install the necessary dependencies:

```bash
pip install -r requirements.txt
```

### 5. Set up environment variables:
Create a `.env` file in the root directory of the project and add the following variables:

```plaintext
SECRET_KEY="YOUR APPLICATION SECRET KEY"
MONGO_URL="YOUR MONGODB URL"
Gemini_API_KEY="YOUR Gemini API KEY"
ALGORITHM="Your Algorithm"
DJANGO_API_URL="Your URL"

```

Replace the placeholder values with your actual credentials.

### 6. Run the application:
Start the application using the following command:

```bash
uvicorn main:app --reload
```

This will run the application in development mode, and you can access it at:

```
http://127.0.0.1:8000
```


