from dotenv import load_dotenv
load_dotenv()
import uuid
import os
import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError
from datetime import date

session = boto3.Session()
region = session.region_name
print(f'Using region: ', {region})

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
    # Haiku
    # 0.06s
    router("Is this a scam? Congratulation, you've won $10M, give me your bank info.")
    
    # 0.07s
    # router("what product can help me with scam protection?")

    # 0.07s
    # router("I need to chat with a live support agent")
    
    # 0.07s
    # router("How many days in a year?")