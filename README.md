# Flask DynamoDB Prompt Responses

A simple Flask application that displays rows of data from DynamoDB, showing prompts and their historical responses with timestamps.

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` with your AWS credentials and configuration
4. Ensure your DynamoDB table exists with the following structure:
   - Primary key: `id` (String)
   - GSI: `PromptIndex` with partition key `prompt` (String)
   - Other attributes: `responses` (List), `timestamp` (String)

## DynamoDB Table Setup

You can create the required DynamoDB table using the AWS CLI:

```bash
aws dynamodb create-table \
    --table-name PromptResponses \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=prompt,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --global-secondary-indexes \
        "[{\"IndexName\": \"PromptIndex\",\"KeySchema\": [{\"AttributeName\": \"prompt\",\"KeyType\": \"HASH\"}],\"Projection\": {\"ProjectionType\": \"ALL\"},\"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5,\"WriteCapacityUnits\": 5}}]"
```

## Local Development with DynamoDB Local

For local development, you can use DynamoDB Local:

1. Download and run DynamoDB Local:
   ```bash
   docker run -p 8000:8000 amazon/dynamodb-local
   ```

2. Set `USE_LOCAL_DYNAMODB=True` in your `.env` file

3. Run the mock data script to create the table and populate it with sample data:
   ```bash
   python mock_data.py
   ```

4. Run the application as usual

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