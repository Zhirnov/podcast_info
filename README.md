# Podcast Transcription and Analysis Application

This repository contains a comprehensive podcast transcription and analysis application. It enables you to transcribe and analyze podcast episodes, extracting summaries, highlights, insights, and more. The application is designed to run on the Modal platform, utilizing various APIs, including OpenAI and SerpApi, to deliver accurate and insightful results.

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Usage](#usage)
- [Deployment](#deployment)
- [Cost Considerations](#cost-considerations)
- [License](#license)

## Introduction

This podcast transcription and analysis application provides an interactive way to transcribe, summarize, and analyze podcast episodes. The backend is powered by the Modal platform, utilizing the Whisper model for transcription and the GPT-3.5 Turbo model for analysis. The frontend is built using Streamlit, offering an intuitive user interface for interacting with the application.

## Getting Started

### Prerequisites

Before setting up and running the application, ensure you have the following:

- A [Modal](https://modal.com) account for running and deploying backend functions.
- [OpenAI API key](https://openai.com/blog/openai-api) for text generation.
- [SerpApi](https://serpapi.com/?gclid=Cj0KCQjw3JanBhCPARIsAJpXTx78k8GCW5JfUQAA7jCIwvrNXqOxeT-3lVTvFknAOOGX9rWQmuCCdR8aAoK4EALw_wcB) API key for fetching guest information.
- Python and pip installed on your local machine.

### Backend Setup

1. Start by checking the backend function on Modal:
   - Create secrets for your OpenAI and Serpapi API keys in your Modal workspace.
   - Run and test the backend function using the following command:
     ```
     !modal run /podcast_backend.py --url <RSS_FEED_URL> --path /content/podcast/
     ```
     Replace `<RSS_FEED_URL>` with the actual RSS feed URL.
   - Once satisfied with the testing, proceed to deploy the backend using the command:
     ```
     !modal deploy /podcast_backend.py
     ```

### Frontend Setup

1. Check the frontend using Streamlit:
   - Clone this repository to your local machine.
   - Navigate to the repository's root directory.
   - Install the required Python packages:
     ```
     pip install -r requirements.txt
     ```
   - Set your Modal token:
     ```
     !modal token set --token-id <TOKEN_ID> --token-secret <TOKEN_SECRET>
     ```
     Replace `<TOKEN_ID>` and `<TOKEN_SECRET>` with your actual Modal token id and secret.
   - Run the Streamlit application:
     ```
     streamlit run podcast_frontend.py
     ```
   - Interact with the frontend interface to select, process, and analyze podcast episodes.

## Usage

1. Choose an existing podcast feed or process a new episode:
   - The frontend dashboard displays a list of available podcast feeds.
   - Select an existing podcast to view its latest episode information and analysis.
   - Process a new episode by entering the RSS feed URL and clicking the "Process Podcast Feed" button.

<img src="https://github.com/Zhirnov/podcast_info/assets/35246537/06aa29fe-dcea-4dc4-b517-3a6424aabca7" width="700">

2. View episode information and analysis:
   - For existing podcasts, the dashboard displays episode details, guest information, summary, highlights, insights, and recommendations.
   - For new episodes, the application processes the episode and presents the information as mentioned above.

<img src="https://github.com/Zhirnov/podcast_info/assets/35246537/9ed8d3e5-a360-4d76-a8cb-ff249070c707" width="700"> <img src="https://github.com/Zhirnov/podcast_info/assets/35246537/3c384fdb-6d48-41d2-bbda-2cb0b0d8d96b" width="700">

## Deployment

1. The backend is deployed on the Modal platform:
   - Ensure you have completed the backend setup and deployment steps mentioned earlier.

2. The frontend is deployed using Streamlit Sharing:
   - Create an account on [Streamlit Sharing](https://www.streamlit.io/sharing).
   - Deploy your frontend application, providing the Modal API token-id and token-secret when prompted.

## Preview how it might look like
https://podcastinfo-afydxya9tb5nvcvkvcmzgp.streamlit.app/

## Cost Considerations

Please be aware of the potential costs associated with using APIs such as OpenAI, Serpapi, and the Modal platform. Usage of these services may incur charges based on API usage and compute resources.

## License

This project is licensed under the [MIT License](LICENSE).
