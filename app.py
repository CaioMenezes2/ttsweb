from flask import Flask, render_template, request, send_file
import pyttsx3
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/audio'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_available_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    # Group voices by language
    voices_by_language = {}
    
    # Language detection patterns
    language_patterns = {
        'English': ['english', 'en-', 'en_', 'eng'],
        'Spanish': ['spanish', 'es-', 'es_', 'spa'],
        'Portuguese': ['portuguese', 'pt-', 'pt_', 'por'],
        'French': ['french', 'fr-', 'fr_', 'fra'],
        'German': ['german', 'de-', 'de_', 'deu'],
        'Italian': ['italian', 'it-', 'it_', 'ita'],
        'Japanese': ['japanese', 'ja-', 'ja_', 'jpn'],
        'Korean': ['korean', 'ko-', 'ko_', 'kor'],
        'Chinese': ['chinese', 'zh-', 'zh_', 'cmn', 'yue'],
        'Russian': ['russian', 'ru-', 'ru_', 'rus'],
    }
    
    for i, voice in enumerate(voices):
        lang = None
        name_lower = voice.name.lower()
        
        # Try to extract language from voice ID first (more reliable)
        if hasattr(voice, 'id'):
            voice_id = voice.id.lower()
            
            # Check for language codes in voice ID
            for language, patterns in language_patterns.items():
                if any(pattern in voice_id for pattern in patterns):
                    lang = language
                    break
            
            # Try to extract language code from Microsoft TTS format
            if not lang and '_' in voice_id:
                parts = voice_id.split('_')
                for part in parts:
                    if '-' in part and len(part) >= 4:  # Looking for patterns like 'en-us'
                        code = part.split('-')[0].lower()
                        for language, patterns in language_patterns.items():
                            if any(pattern.startswith(code) for pattern in patterns):
                                lang = language
                                break
                        if lang:
                            break
        
        # Fallback to name-based detection if language not found in ID
        if not lang:
            # Check for language name in voice name
            for language, patterns in language_patterns.items():
                if any(pattern in name_lower for pattern in patterns):
                    lang = language
                    break
            
            # Try to extract language from voice name format "Language: Voice Name"
            if not lang and ':' in voice.name:
                prefix = voice.name.split(':')[0].strip().lower()
                for language, patterns in language_patterns.items():
                    if any(pattern in prefix for pattern in patterns):
                        lang = language
                        break
        
        # If still no language detected, mark as Other
        if not lang:
            lang = 'Other'
        
        if lang not in voices_by_language:
            voices_by_language[lang] = []
        voices_by_language[lang].append((i, voice.name))
    
    # Sort languages alphabetically
    return dict(sorted(voices_by_language.items()))

def convert_text_to_speech(text, voice_id):
    if not text or not isinstance(voice_id, int):
        raise ValueError('Invalid text or voice ID provided')

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        if voice_id >= len(voices):
            raise ValueError(f'Voice ID {voice_id} is not available')
            
        engine.setProperty('voice', voices[voice_id].id)
        engine.setProperty('rate', 150)
        
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], 'output.wav')
        
        # Clear any existing file
        if os.path.exists(output_file):
            os.remove(output_file)
        
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        
        # Verify the file exists and has content with timeout
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return output_file
            time.sleep(0.5)
            attempt += 1
            
        raise Exception('Timeout: Failed to generate audio file')
        
    except Exception as e:
        if os.path.exists(output_file):
            os.remove(output_file)
        raise Exception(f'Error generating audio: {str(e)}')


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        voices = get_available_voices()
        app.logger.info(f'Found {sum(len(v) for v in voices.values())} voices across {len(voices)} languages')
    except Exception as e:
        app.logger.error(f'Error loading voices: {str(e)}')
        voices = {}
    
    if request.method == 'POST':
        text = request.form['text']
        voice_id = int(request.form['voice'])
        
        try:
            output_file = convert_text_to_speech(text, voice_id)
            return send_file(output_file, mimetype='audio/wav')
        except Exception as e:
            app.logger.error(f'Error in text-to-speech conversion: {str(e)}')
            return str(e), 500
    
    return render_template('index.html', voices=voices)

if __name__ == '__main__':
    app.run(debug=True)