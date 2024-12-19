from flask import Flask, request, jsonify, send_from_directory, render_template
from transformers import pipeline
from gtts import gTTS
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
import os
import requests
from bs4 import BeautifulSoup
import random
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
import traceback
import openai

app = Flask(__name__)
openai.api_key = "Ysk-proj-vuKyb1P7opp36rRxbv8ukbzzXOiBxmrRZAaI30IBbndUG_VhCoemSp1YqCnOJXF2kY6DZ_orsYT3BlbkFJDACiVELFhNmYxcIQJSXOFoPNgkNn-rZlZNEARcjjDKAgYC_nASA4lKb8m8Bpr3Y4tEvnRgMMAA"  


summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


os.makedirs('static/output', exist_ok=True)
os.makedirs('static/slides', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize')
def summarize():
    return render_template('summarize.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    return jsonify({"message": "Quiz submitted successfully!"})

@app.route('/static/output/<path:filename>')
def download_file(filename):
    return send_from_directory('static/output', filename)


def scrape_google_images(query):
    query = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}&source=lnms&tbm=isch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    image_elements = soup.find_all("img")
    image_urls = [img['src'] for img in image_elements if 'src' in img.attrs and img['src'].startswith("http")]
    return image_urls[0] if image_urls else None

def create_slides(text, slide_number):
    slide_image = f'static/slides/slide_{slide_number}.png'
    keywords = text.split()[:4]
    prompt = ' '.join(keywords)
    image_url = scrape_google_images(prompt)

    if image_url:
        img_response = requests.get(image_url)
        with open(slide_image, 'wb') as img_file:
            img_file.write(img_response.content)
        img = Image.open(slide_image)
    else:
        img = Image.new('RGB', (1280, 720), color=(random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)))

    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 40)
    except:
        font = ImageFont.load_default()

    margin, offset = 50, 100
    max_chars_per_line = 40
    wrapped_lines = [text[i:i+max_chars_per_line] for i in range(0, len(text), max_chars_per_line)]
    for line in wrapped_lines:
        d.text((margin, offset), line, font=font, fill=(0, 0, 0))
        offset += 50

    img.save(slide_image)
    return slide_image

def generate_audio(text, file_path):
    tts = gTTS(text)
    tts.save(file_path)

def create_video_with_transitions(slides, audio_file, slide_duration=6):
    clips = [ImageClip(slide).set_duration(slide_duration).fadein(0.5).fadeout(0.5) for slide in slides]
    video_clip = concatenate_videoclips(clips, method='compose')
    audio = AudioFileClip(audio_file)
    video_with_audio = video_clip.set_audio(audio)
    if audio.duration > video_with_audio.duration:
        last_slide_duration = audio.duration - video_with_audio.duration
        last_clip = clips[-1].set_duration(last_slide_duration)
        clips[-1] = last_clip
        video_with_audio = concatenate_videoclips(clips, method='compose').set_audio(audio)
    video_output_path = 'static/output/video_lecture.mp4'
    video_with_audio.write_videofile(video_output_path, fps=24, codec='libx264', bitrate="5000k", audio_codec='aac')
    return video_output_path

def chunk_text(text, chunk_size=1024):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

@app.route('/text_to_video', methods=['POST'])
def text_to_video():
    try:
        data = request.get_json()
        text = data.get('text')
        chunks = chunk_text(text)
        summary_list = [summarizer(chunk, min_length=100, max_length=300, do_sample=False)[0]['summary_text'] for chunk in chunks]
        full_summary = ' '.join(summary_list)
        audio_file = 'static/output/output_audio.mp3'
        generate_audio(full_summary, audio_file)
        slide_texts = [' '.join(full_summary.split(' ')[i:i + 15]) for i in range(0, len(full_summary.split(' ')), 15)]
        slides = [create_slides(slide_text, i + 1) for i, slide_text in enumerate(slide_texts)]
        video_output_path = create_video_with_transitions(slides, audio_file)
        return jsonify({"summary": full_summary, "video_file": video_output_path})
    except Exception as e:
        print(traceback.format_exc())
        return str(e), 500

@app.route('/youtube_to_text', methods=['POST'])
def youtube_to_text():
    try:
        data = request.get_json()
        video_url = data.get('url')
        match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})", video_url)
        if not match:
            return jsonify({"error": "Invalid YouTube URL"}), 400
        video_id = match.group(1)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except (TranscriptsDisabled, NoTranscriptFound):
            return jsonify({"error": "Transcript not available for this video."}), 400
        full_transcript = " ".join([entry['text'] for entry in transcript])
        chunks = chunk_text(full_transcript, 1000)
        summarized_transcript = ' '.join([summarizer(chunk, min_length=50, max_length=150, do_sample=False)[0]['summary_text'] for chunk in chunks])
        return jsonify({"transcript": full_transcript, "summary": summarized_transcript})
    except Exception as e:
        print(traceback.format_exc())
        return str(e), 500

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    text = data.get('text')
    prompt = f"Generate 5 quiz questions based on the following text:\n\n{text}\n\nQuestions:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7
    )
    questions = response['choices'][0]['message']['content'].strip().split("\n")
    return jsonify({"questions": questions})

@app.route('/evaluate_quiz', methods=['POST'])
def evaluate_quiz():
    data = request.get_json()
    user_answers = data.get('answers')
    correct_answers = data.get('correct_answers')
    score = sum(1 for user_answer, correct_answer in zip(user_answers, correct_answers) if user_answer.strip().lower() == correct_answer.strip().lower())
    return jsonify({"score": score, "total": len(correct_answers)})

if __name__ == "__main__":
    app.run(debug=True)
