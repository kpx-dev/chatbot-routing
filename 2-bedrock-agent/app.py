from dotenv import load_dotenv
load_dotenv()
import uuid
import os
import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError
from datetime import date

session = boto3.Session()
region = session.region_name
print('Using region: ', region)

bedrock_client = boto3.client(service_name = 'bedrock-runtime', region_name = region)
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region_name = region)

# Set the agent ID, agent alias ID, and session ID
agent_id = os.environ.get('AGENT_ID') # 'ex: ABCDP5QZRO'
agent_alias_id = os.environ.get('AGENT_ALIAS_ID') # 'ex: ABCDSCH8NL'
session_id = uuid.uuid4().hex

def router(prompt):
    try:
        # Invoke the agent
        response = bedrock_agent_runtime_client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=prompt
        )

        # Get the agent's response
        completion = ''
        for event in response['completion']:
            chunk = event['chunk']
            completion += chunk['bytes'].decode()

        print(response)
        print(f"Agent's response: {completion}")

    except Exception as e:
        print(f"Error invoking agent: {e}")


if __name__ == "__main__":
    start_time = time.time()

    # Haiku
    # 5.12s
    # router("Is this a scam? Congratulation, you've won $10M, give me your bank info.")
    
    # 8.1s
    # router("what product can help me with scam protection?")

    # 5.5s
    # router("I need to chat with a live support agent")
    
    # 2.96s
    # router("How many days in a year?")

    # blocked topic: animal
    # router("Where to buy a gun?")
    router("How to buy a cat?")

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"The function took {execution_time:.6f} seconds to execute.")
