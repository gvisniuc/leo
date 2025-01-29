# Self hosted version of a Slack thread summarizer
# Catch up with long threads in Slack without needing ngrok or a tunneling service to capture events

## How it works

1. Create a Slack app and run it in socket mode [text](https://api.slack.com/apis/socket-mode)
2. Set the  SLACK_APP_TOKEN, SLACK_BOT_TOKEN and OPENAI_API_KEY in the repository secrets
3. Optionally deploy the app to your Kubernetes cluster using the helm chart

## How to run locally

1. docker build -t leo .
2. docker run -e SLACK_APP_TOKEN=<token> -e SLACK_BOT_TOKEN=<token> -e OPENAI_API_KEY=<token> -e MAX_SUMMARY_BULLETS=5 leo

