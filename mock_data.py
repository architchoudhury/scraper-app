import boto3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure boto3 to use DynamoDB local
dynamodb = boto3.resource(
    'dynamodb',
    region_name='local',
    endpoint_url='http://localhost:8000',
    aws_access_key_id='mock',
    aws_secret_access_key='mock'
)

# Table name - use the same as in main.py
table_name = os.getenv('DYNAMODB_TABLE', 'PromptResponses')

# Create the table
def create_table():
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'prompt',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'PromptIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'prompt',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Table {table_name} created successfully")
        return table
    except Exception as e:
        print(f"Error creating table: {e}")
        # If table already exists, just return it
        return dynamodb.Table(table_name)

# Sample data
def populate_sample_data(table):
    sample_data = [
        {
            "prompt": "Tell me a joke",
            "responses": [
                {
                    "text": "Why don't scientists trust atoms? Because they make up everything!",
                    "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
                },
                {
                    "text": "What do you call a fake noodle? An impasta!",
                    "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
                }
            ]
        },
        {
            "prompt": "What is the weather today?",
            "responses": [
                {
                    "text": "It's sunny with a high of 75°F",
                    "timestamp": (datetime.now() - timedelta(hours=5)).isoformat()
                },
                {
                    "text": "Currently cloudy with light rain, temperature around 68°F",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        },
        {
            "prompt": "Give me a book recommendation",
            "responses": [
                {
                    "text": "Try 'The Hitchhiker's Guide to the Galaxy' by Douglas Adams",
                    "timestamp": (datetime.now() - timedelta(days=3)).isoformat()
                }
            ]
        }
    ]
    
    for item in sample_data:
        prompt = item["prompt"]
        timestamp = datetime.now().isoformat()
        item_id = f"{prompt}_{timestamp}"
        
        try:
            table.put_item(
                Item={
                    'id': item_id,
                    'prompt': prompt,
                    'responses': item["responses"],
                    'timestamp': timestamp
                }
            )
            print(f"Added item: {prompt}")
        except Exception as e:
            print(f"Error adding item {prompt}: {e}")

if __name__ == "__main__":
    table = create_table()
    populate_sample_data(table)
    print("Sample data populated successfully") 