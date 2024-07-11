from dotenv import load_dotenv
load_dotenv()
import boto3
import time 
import json 
import os 

session = boto3.Session()
region = session.region_name
print(f'Using region: ', {region})

# Create a Lex Runtime client
lex_client = boto3.client(service_name = 'lexv2-runtime', region_name = region)

bot_id = os.environ.get('LEX_BOT_ID') # 'ex: ABCWNJ5VR0'
bot_alias_id = os.environ.get('LEX_BOT_ALIAS_ID') # 'ex: ABCFDO0YC2'
locale_id='en_US'
session_id='test-poc-session'

def router(query):
    try:
        # Send a text message to the bot
        response = lex_client.recognize_text(
            botId=bot_id,
            botAliasId=bot_alias_id,
            localeId=locale_id,
            sessionId=session_id,
            text=query
        )
        print("Intent detected as: " , response['sessionState']['intent']['name'])
        # print(json.dumps(response['interpretations']))
    except Exception as e:
        print(f"Error invoking Lex bot: {e}")

if __name__== "__main__":
    start_time = time.time()

    router("Is this a scam? Congratulation, you've won $10M, give me your bank info.")
    # router("what product can help me with scam protection?")
    # router("I need to chat with a live support agent")
    # router("How many days in a year?")

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"The function took {execution_time:.6f} seconds to execute.")