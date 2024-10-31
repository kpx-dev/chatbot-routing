from dotenv import load_dotenv
load_dotenv()
import boto3
import os
import json
from datetime import datetime
from botocore.exceptions import ClientError
from datetime import date

session = boto3.Session()
region = session.region_name

# modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
modelId = 'anthropic.claude-3-haiku-20240307-v1:0'

print(f'Using modelId: {modelId}')
print(f'Using region: ', {region})

bedrock_client = boto3.client(service_name = 'bedrock-runtime', region_name = region)

def provider_scam_detection(query):
    print(f"Scam detection provider: {query}")

def provider_product_question(query):
    print(f"Product question provider: {query}")

def provider_support_question(query):
    print(f"Support question provider: {query}")

def provider_catch_all(query):
    print(f"Catch-all / fallback provider: {query}")

provider_scam_detection_schema = {
    "toolSpec": {
        "name": "provider_scam_detection",
        "description": "A tool to detect whether an input is a scam or not.",
        "inputSchema": {
            "json": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The user query that might contain the scam message"}
            },
            "required": ["query"]
            }
        }
    }
}

provider_product_question_schema = {
    "toolSpec": {
        "name": "provider_product_question",
        "description": "A tool to answer product questions, how a product can help protect customer.",
        "inputSchema": {
            "json": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The user query that contain question about products"}
            },
            "required": ["query"]
            }
        }
    }
}

provider_support_question_schema = {
    "toolSpec": {
        "name": "provider_support_question",
        "description": "A tool to answer support related questions, or assistant needed from a live human.",
        "inputSchema": {
            "json": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The user query that contain support questions, potentially needing help from live human"}
            },
            "required": ["query"]
            }
        }
    }
}

provider_catch_all_schema = {
    "toolSpec": {
        "name": "provider_catch_all",
        "description": "A tool to handle any generic query that other previous tools can't answer.",
        "inputSchema": {
            "json": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The user query that other previous tool doesn't understand."}
            },
            "required": ["query"]
            }
        }
    }
}

toolConfig = {
    "tools": [provider_scam_detection_schema, provider_product_question_schema, provider_support_question_schema, provider_catch_all_schema],
    "toolChoice": {
        "any":{},    # must trigger one of the available tools
        # "auto":{}, # default
        # "tool":{   # always trigger this tool
        #     "name": "provider_scam_detection"
        # },
    }
}

def guardrails(prompt): 
    response = bedrock_client.apply_guardrail(
        guardrailIdentifier=os.environ.get('GUARDRAILS_ID'), # ex: '453cg26ykbxy'
        guardrailVersion='1',
        source='INPUT', #|'OUTPUT',
        content=[
            {
                'text': {
                    'text': prompt,
                    # 'qualifiers': [
                    #     'grounding_source'|'query'|'guard_content',
                    # ]
                }
            },
        ]
    )
    # print(response)
    return response 
    
def router(user_query, enable_guardrails=False):
    # apply guardrails 
    if enable_guardrails:
        guard = guardrails(user_query)
        if guard['action'] == 'GUARDRAIL_INTERVENED':
            print("Guardrails blocked this action", guard["assessments"])
            return

    messages = [{"role": "user", "content": [{"text": user_query}]}]

    system_prompt=f"""
        Break down the user questions and match each question to a tool.
        Always return at least 2 tools.
    """

    converse_api_params = {
        "modelId": modelId,
        "system": [{"text": system_prompt}],
        "messages": messages,
        "inferenceConfig": {"temperature": 0.0, "maxTokens": 4096},
        "toolConfig": toolConfig,        
        "guardrailConfig": {
            "guardrailIdentifier": "xyz",
            "guardrailVersion": "1",
            "trace": "enabled"
        }
    }

    response = bedrock_client.converse(**converse_api_params)
    # print(response)

    stop_reason = response['stopReason']

    if stop_reason == "end_turn":
        print("Claude did NOT call a tool")
        print(f"Assistant: {stop_reason}")
    elif stop_reason == "tool_use":
        print("Claude wants to use a tool")
        print(stop_reason)
        print(response['output'])
        print(response['usage'])
        print(response['metrics'])
        

if __name__ == "__main__":
    # example of triggering 2 tools in 1 user prompt: 
    # output: {'message': {'role': 'assistant', 'content': [{'toolUse': {'toolUseId': 'tooluse_abc', 'name': 'provider_scam_detection', 'input': {'query': 'what product can help me with scam protection'}}}, {'toolUse': {'toolUseId': 'tooluse_cde', 'name': 'provider_support_question', 'input': {'query': 'I need to talk to live human support'}}}]}}
    router("what product can help me with scam protection and I need to talk to live human support")

    # blocked by Guardrails due to animal topic
    # router("where to buy dog?", enable_guardrails=True)

    # Haiku
    # {'message': {'role': 'assistant', 'content': [{'toolUse': {'toolUseId': 'tooluse_xyz', 'name': 'provider_scam_detection', 'input': {'query': "Congratulation, you've won $10M, give me your bank info."}}}]}}
    # {'inputTokens': 841, 'outputTokens': 56, 'totalTokens': 897}
    # {'latencyMs': 889}    
    # router("Is this a scam? Congratulation, you've won $10M, give me your bank info.")

    # Haiku
    # {'message': {'role': 'assistant', 'content': [{'toolUse': {'toolUseId': 'tooluse_xyz', 'name': 'provider_product_question', 'input': {'query': 'what product can help me with scam protection?'}}}]}}
    # {'inputTokens': 828, 'outputTokens': 49, 'totalTokens': 877}
    # {'latencyMs': 828}
    # router("what product can help me with scam protection?")

    # Haiku 
    # {'message': {'role': 'assistant', 'content': [{'toolUse': {'toolUseId': 'tooluse_xyz', 'name': 'provider_support_question', 'input': {'query': 'I need to chat with a live support agent'}}}]}}
    # {'inputTokens': 827, 'outputTokens': 48, 'totalTokens': 875}
    # {'latencyMs': 646}
    # router("I need to chat with a live support agent")

    # Haiku 
    # {'message': {'role': 'assistant', 'content': [{'toolUse': {'toolUseId': 'tooluse_xyz', 'name': 'provider_catch_all', 'input': {'query': 'How many days in a year?'}}}]}}
    # {'inputTokens': 825, 'outputTokens': 46, 'totalTokens': 871}
    # {'latencyMs': 798}
    # router("How many days in a year?")