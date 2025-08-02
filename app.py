from flask import Flask, render_template, request, send_from_directory
import os
import yt_dlp
from demucs.apply import apply_model
from demucs.pretrained import get_model
from demucs.audio import AudioFile

app = Flask(__name__)
STEM_DIR = 'stems'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        os.makedirs(STEM_DIR, exist_ok=True)
        info = download_audio(url)
        stem_paths = separate_stems(info['filepath'])
        return render_template('index.html', stems=stem_paths)
    return render_template('index.html', stems=None)

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(STEM_DIR, '%(title)s.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    filepath = ydl.prepare_filename(info)
    return {'filepath': filepath}

def separate_stems(filepath):
    model = get_model('demucs')  # adjust model name/version
    apply_model(model, [filepath], out_dir=STEM_DIR, split=True)
    base = os.path.splitext(os.path.basename(filepath))[0]
    return [f"{STEM_DIR}/{base}/{stem}.wav" for stem in ['vocals','drums','bass','other']]

@app.route('/stems/<path:filename>')
def download_file(filename):
    return send_from_directory(STEM_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
