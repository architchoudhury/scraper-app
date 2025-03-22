# Flask DynamoDB Prompt Responses

A simple Flask application that displays rows of data from DynamoDB, showing prompts and their historical responses with timestamps.

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` with your AWS region configuration (us-east-2)
4. Ensure your AWS CLI is properly configured with credentials that have access to DynamoDB

## DynamoDB Table Structure

The application expects a DynamoDB table named 'PromptResponses' with the following structure:
- Each item contains:
  - `prompt` (String): The prompt text
  - `response` (String): The response text
  - `timestamp` (String): ISO-formatted timestamp
- Table should be in us-east-2 region

## Running the Application

```bash
python main.py
```

Then visit http://127.0.0.1:5000/ in your browser.

## Features

- View all prompts and their historical responses
- Add new responses to existing prompts
- Create new prompts with responses
- Timestamps for all responses 