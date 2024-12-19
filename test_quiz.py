from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('quiz.html')

# Route to generate quiz questions
@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    text = data.get("text")
    
    # Simulate generating questions from text
    questions = [
        "What is Artificial Intelligence?",
        "What do machines simulate in AI?",
        "What kind of intelligence is simulated in AI?",
        "AI processes include what?",
        "AI involves the simulation of what?"
    ]
    return jsonify({"questions": questions})

# Route to evaluate quiz answers
@app.route('/evaluate_quiz', methods=['POST'])
def evaluate_quiz():
    data = request.get_json()
    user_answers = data.get("answers")
    correct_answers = data.get("correct_answers")

    # Calculate score
    score = sum(1 for ua, ca in zip(user_answers, correct_answers) if ua == ca)
    return jsonify({"score": score, "total": len(correct_answers)})

if __name__ == "__main__":
    app.run(debug=True)
