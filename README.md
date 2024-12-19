# CramCast

CramCast is a study aid application that converts text and YouTube lecture videos into summarized video lectures with accompanying slides and audio. It also generates quizzes based on the summaries to help users test their understanding.

## Features

- **Summarize Text to Video**: Input lengthy text, and the app will generate a video with slides and an audio narration of the summarized content.
- **YouTube to Summary**: Extract transcripts from YouTube videos, summarize them, and optionally convert them into videos.
- **Quiz Generation**: Create quizzes based on the summarized content to reinforce learning.
- **Downloadable Outputs**: Videos and quizzes are available for download.

---

## Technologies Used

- **Backend**: Python, Flask
- **AI Models**: Hugging Face Transformers (`facebook/bart-large-cnn`), OpenAI GPT-4
- **Utilities**: gTTS (Text-to-Speech), MoviePy (Video Creation), YouTube Transcript API
- **Frontend**: HTML, CSS, JavaScript
- **Database**: None (in-memory operations for simplicity)

---

## Prerequisites

1. Python 3.7 or later
2.pip install -r requirements.txt

---

## Installation and Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/cramcast.git
   cd cramcast

##Run the project 
python app.py

