import os
import asyncio
from openai import AsyncOpenAI
import requests


def read_api_key(filepath):
    with open(filepath, "r") as file:
        return file.read().strip()


# Function to get pollen data from the API
def get_pollen_data(location, google_api_key):
    endpoint = f"https://pollen.googleapis.com/v1/forecast:lookup?location={location}&key={google_api_key}"
    response = requests.get(endpoint)

    if response.status_code == 200:
        return response.json()
    else:
        return f"Error fetching data: {response.status_code}"


def extract_location(user_input):
    # Basic implementation: assume the user says "pollen info in [location]"
    if "pollen info in" in user_input.lower():
        location = user_input.lower().split("pollen info in ")[1]
        return location
    return None


async def chat_with_openai(client, messages):
    completion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion.choices[0].message.content


async def main():
    # Read the API keys
    openai_api_key = read_api_key(
        "/Users/osagiealonge/My Drive/School/IronHack/Projects/Web Scraper/Final Project/cgptkey.txt")
    google_api_key = read_api_key(
        "/Users/osagiealonge/My Drive/School/IronHack/Projects/Web Scraper/Final Project/googleapikey.txt")

    os.environ["OPENAI_API_KEY"] = openai_api_key
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    message_history = []

    def read_task_description(file_path):
        with open(file_path, 'r') as file:
            return file.read().strip()

    task_file_path = '/Users/osagiealonge/My Drive/School/IronHack/Projects/Web Scraper/Final Project/clara_task.txt'
    task_description = read_task_description(task_file_path)

    initial_message = {"role": "user",
                       "content": task_description
                       }
    message_history.append(initial_message)

    reply_content = await chat_with_openai(client, message_history)

    sentences = reply_content.split('. ')  # Split the text into sentences
    compact_reply = '\n'.join(sentences)  # Join the sentences with a newline character
    print(compact_reply)

    message_history.append({"role": "assistant", "content": reply_content})

    for _ in range(10):
        user_input = input("> ")
        # Directly append the user input to the message history without printing "User's input is:"
        message_history.append({"role": "user", "content": user_input})

        reply_content = await chat_with_openai(client, message_history)

        sentences_cont = reply_content.split('. ')

        # Format the reply content to be compact before printing
        compact_reply = '\n'.join(sentences_cont)
        print(compact_reply)

        # Remember to append the compact version of the reply to the message history
        message_history.append({"role": "assistant", "content": compact_reply})

        if "pollen info in" in user_input.lower():
            location = extract_location(user_input)
            if location:
                pollen_data = get_pollen_data(location, google_api_key)
                # Format and print the pollen data
                print(pollen_data)  # You might need to format this better based on the data structure
            else:
                print("Sorry, I couldn't find the location in your query.")
        else:
            message_history.append({"role": "user", "content": user_input})
            reply_content = await chat_with_openai(client, message_history)
            #print(reply_content)
            message_history.append({"role": "assistant", "content": reply_content})


# Run the main coroutine
if __name__ == "__main__":
    asyncio.run(main())
