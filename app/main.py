import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Install the Slack app and get xoxb- token in advance
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# Add functionality here
import openai
BOT_USER_ID = app.client.auth_test()["user_id"]


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_thread(messages, possible_prompt):
    """
    Use OpenAI to summarize the thread.
    :param messages: List of messages from the thread.
    :return: A summary string.
    """

    thread_text = "\n".join([
        f"{get_user_name(msg.get('user'))}: {msg.get('text')}" 
        for msg in messages 
        if msg.get('text') and not msg.get('text').startswith(f'<@{BOT_USER_ID}>') and msg.get('user') != BOT_USER_ID
    ])

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes Slack conversations concisely."},
                {"role": "user", "content": f"Taking into account the following user instructions: {possible_prompt} if it makes sense, summarize the following Slack thread in maximum {os.getenv('MAX_SUMMARY_BULLETS', 5)} bullet points:\n\n{thread_text}"}
            ],
            temperature=os.getenv("OPENAI_TEMPERATURE", 0.5),
        )

        
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"Error summarizing thread: {e}")
        return "Sorry, I couldn't summarize the thread due to an error."


def get_user_name(user_id):
    """
    Retrieve the username or display name for a given user ID.
    :param user_id: Slack user ID.
    :return: The user's real name or display name.
    """
    try:
        response = app.client.users_info(user=user_id)
        user_info = response.get("user", {})
        # Prefer the display name, fallback to real name
        return user_info.get("profile", {}).get("display_name") or user_info.get("real_name") or user_id
    except Exception as e:
        print(f"Error fetching user info for {user_id}: {e}")
        return user_id  # Fallback to user ID if error occurs
    
@app.event("app_mention")
def handle_app_mention(body, say):
    event = body.get("event", {})
    channel_id = event.get("channel")
    thread_ts = event.get("thread_ts", event.get("ts"))  # Use thread_ts if available, otherwise ts
    user_id = event.get("user")

    possible_prompt = event.get("text")
    

    if not channel_id or not thread_ts:
        return

    # Fetch the thread
    try:
        result = app.client.conversations_replies(channel=channel_id, ts=thread_ts)

        logger.info("Received event")
        messages = result.get("messages", [])
        
        logger.info("Summarizing thread")

        if len(messages) > 1:
          # Summarize the thread using OpenAI
          summary = summarize_thread(messages, possible_prompt)

          # Respond with the summary in the same thread
          say(
              text=f"Hi <@{user_id}>! Here's the summary of the thread:\n\n{summary}",
              channel=channel_id,
              thread_ts=thread_ts
          )
        
        else:
          say(
              text=f"Hi <@{user_id}>! There are no messages in this thread",
              channel=channel_id,
              thread_ts=thread_ts
          )
    except Exception as e:
        logger.error(f"Error handling app mention: {e}")

if __name__ == "__main__":
    # Create an app-level token with connections:write scope
    handler = SocketModeHandler(app=app, app_token=os.getenv("SLACK_APP_TOKEN"))
    handler.start()
