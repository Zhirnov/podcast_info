import modal
import os
import whisper
import openai
from langchain.chat_models import ChatOpenAI
import tiktoken
import json
from langchain.agents import (
    load_tools,
    initialize_agent,
    AgentType,
)


def download_whisper():
    # Load the Whisper model
    print("Download the Whisper model")

    # Perform download only once and save to Container storage
    whisper._download(whisper._MODELS["medium"], "/content/podcast/", False)


stub = modal.Stub("corise-podcast-project")
corise_image = (
    modal.Image.debian_slim()
    .pip_install(
        "feedparser",
        "https://github.com/openai/whisper/archive/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d.tar.gz",
        "requests",
        "ffmpeg",
        "openai",
        "tiktoken",
        "langchain",
        "google-search-results",
        "ffmpeg-python",
    )
    .apt_install("ffmpeg")
    .run_function(download_whisper)
)


@stub.function(image=corise_image, gpu="any", timeout=600)
def get_transcribe_podcast(rss_url, local_path):
    print("Starting Podcast Transcription Function")
    print("Feed URL: ", rss_url)
    print("Local Path:", local_path)

    # Read from the RSS Feed URL
    import feedparser

    intelligence_feed = feedparser.parse(rss_url)
    podcast_title = intelligence_feed["feed"]["title"]
    host_name = intelligence_feed.entries[0].author
    episode_duration = intelligence_feed.entries[0].itunes_duration
    episode_title = intelligence_feed.entries[0]["title"]
    episode_image = intelligence_feed["feed"]["image"].href
    for item in intelligence_feed.entries[0].links:
        if item["type"] == "audio/mpeg":
            episode_url = item.href
    episode_name = (intelligence_feed.entries[0].title + ".mp3").replace(" ", "_")
    print("RSS URL read and episode URL: ", episode_url)

    # Download the podcast episode by parsing the RSS feed
    from pathlib import Path

    p = Path(local_path)
    p.mkdir(exist_ok=True)

    print("Downloading the podcast episode")
    import requests

    with requests.get(episode_url, stream=True) as r:
        r.raise_for_status()
        episode_path = p.joinpath(episode_name)
        with open(episode_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print("Podcast Episode downloaded")

    # Load model from saved location
    print("Load the Whisper model")
    model = whisper.load_model(
        "medium", device="cuda", download_root="/content/podcast/"
    )

    # Perform the transcription
    print("Starting podcast transcription")
    result = model.transcribe(local_path + episode_name)

    # Return the transcribed text
    print("Podcast transcription completed, returning results...")
    output = {}
    output["podcast_title"] = podcast_title
    output["host_name"] = host_name
    output["episode_title"] = episode_title
    output["episode_image"] = episode_image
    output["episode_duration"] = episode_duration
    output["episode_transcript"] = result["text"]
    return output


@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_info(podcast_transcript, host_name):
    function_description = [
        {
            "name": "get_podcast_info",
            "description": "Get the summary, guest information, highlights of the main ideas, any insights, actionable recommendations from the podcast transcript",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Get a concise summary of the podcast transcript in 5 sentences. Use engaging style and make it attractive to go and listen to the whole story.",
                    },
                    "guest_name": {
                        "type": "string",
                        "description": "Extract the full name of the podcast guest speaker",
                    },
                    "guest_info": {
                        "type": "string",
                        "description": "Extract the information about the podcast guest, job, title, etc.",
                    },
                    "highlights": {
                        "type": "string",
                        "description": "Extract the highlights of the main ideas discussed in the podcast",
                    },
                    "insights": {
                        "type": "string",
                        "description": "Extract the insights about the topic discussed in the podcast",
                    },
                    "actionable_recommendations": {
                        "type": "string",
                        "description": "Extract the actionable recommendations suggested in the podcast",
                    },
                },
                "required": [
                    "summary",
                    "guest_name",
                    "guest_info",
                    "highlights",
                    "insights",
                    "actionable_recommendations",
                ],
            },
        }
    ]

    instructPrompt = f"You are the helpful assistant of a professional writer. Please extract useful information for my weekly podcast newsletter from the transcript: {podcast_transcript} by the host: {host_name}"
    messages = [{"role": "user", "content": instructPrompt}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        temperature=0,
        messages=messages,
        functions=function_description,
        function_call="auto",
    )
    podcastInfo = json.loads(response.choices[0].message.function_call.arguments)

    return podcastInfo


@stub.function(
    image=corise_image,
    secrets=[
        modal.Secret.from_name("my-openai-secret"),
        modal.Secret.from_name("my-serpapi-secret"),
    ],
    timeout=1200,
)
def get_guest_info(guest_name, guest_info):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=256)
    tools = load_tools(["serpapi"], llm=llm)
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    guest_info = agent.run(
        f"Find information about {guest_name} and write one sentence pitch about this person. You can use this additional information {guest_info}"
    )
    return guest_info


@stub.function(
    image=corise_image, secret=modal.Secret.from_name("my-openai-secret"), timeout=1200
)
def process_podcast(url, path):
    output = {}
    podcast_details = get_transcribe_podcast.remote(url, path)
    podcast_info = get_podcast_info.remote(
        podcast_details["episode_transcript"], podcast_details["host_name"]
    )
    output["podcast_details"] = podcast_details
    output["podcast_summary"] = podcast_info["summary"]

    if podcast_info["guest_name"] != "":
        output["podcast_guest"] = podcast_info["guest_name"]
        output["podcast_guest_info"] = get_guest_info.remote(
            podcast_info["guest_name"], podcast_info["guest_info"]
        )
    else:
        output["podcast_guest"] = ""
        output["podcast_guest_info"] = ""

    output["podcast_highlights"] = podcast_info["highlights"]
    output["podcast_insights"] = podcast_info["insights"]
    output["podcast_actionable_recommendations"] = podcast_info[
        "actionable_recommendations"
    ]

    return output


@stub.local_entrypoint()
def test_method(url, path):
    output = {}
    podcast_details = get_transcribe_podcast.remote(url, path)
    podcast_info = get_podcast_info.remote(
        podcast_details["episode_transcript"], podcast_details["host_name"]
    )
    guest_info = get_guest_info.remote(
        podcast_info["guest_name"], podcast_info["guest_info"]
    )

    print("Podcast Summary: ", podcast_info["summary"])
    if podcast_info["guest_name"] != "":
        print("Podcast Guest Information: ", podcast_info["guest_name"], guest_info)
    else:
        print("There was no guest")

    print("Podcast Highlights: ", podcast_info["highlights"])
    print("Podcast insights: ", podcast_info["insights"])
    print("Actionable recommendations: ", podcast_info["actionable_recommendations"])
