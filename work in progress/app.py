from flask import Flask, render_template, request, jsonify
import whisper
import os

app = Flask(__name__)

# Load model once
model = whisper.load_model("base")

@app.route("/")
def home():
    return render_template("report.html")

@app.route("/voice", methods=["POST"])
def voice():
    if "audio" not in request.files:
        return jsonify({"text": ""})

    audio = request.files["audio"]
    file_path = "temp.wav"
    audio.save(file_path)

    result = model.transcribe(file_path, task="translate")

    os.remove(file_path)

    print("TRANSLATED:", result["text"])

    return jsonify({"text": result["text"].strip()})

if __name__ == "__main__":
    app.run(debug=True)