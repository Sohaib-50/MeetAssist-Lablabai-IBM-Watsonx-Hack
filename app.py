
from flask import Flask, render_template, request
from utils.helpers import get_welcome_message, pre_meeting_analysis, post_meeting_analysis
import os
import random

app = Flask(__name__)

@app.route('/')
def home():
    welcome_message = get_welcome_message()
    return render_template('home.html', message=welcome_message)


@app.route('/pre-meeting')
def pre_meeting():
    return render_template('pre_meeting.html')


@app.route('/post-meeting')
def post_meeting():

    sample_transcript_files = [
        'QMSum-dataset-ES2006a.json.txt',
        'QMSum-dataset-TS3010a.json.txt',
        'QMSum-dataset-IS1006a.json.txt',
        'QMSum-dataset-TS3010d.json.txt'
    ]
    transcript_files = {}
    for filename in sample_transcript_files:
        file_path = f'Transcripts/{filename}'
        if os.path.isfile(file_path):  # Check if the file exists
            with open(file_path, 'r') as file:
                transcript_files[filename] = file.read()

    return render_template('post_meeting.html', transcript_files=transcript_files)


@app.route('/pre-meeting-analysis-result', methods=['POST'])
def pre_meeting_analysis_result():
    
    # get post variables (form data: meeting topic, meeting background, participants)
    meeting_topic = request.form['meeting_topic']
    meeting_background = request.form['meeting_background']
    meeting_participants = request.form['meeting_participants']

    result = pre_meeting_analysis(meeting_topic, meeting_background, meeting_participants)


    return render_template('pre-meeting-analysis-result.html', result=result, meeting_topic=meeting_topic, meeting_background=meeting_background, meeting_participants=meeting_participants)
    

@app.route('/post-meeting-analysis-result', methods=['POST'])
def post_meeting_analysis_result():

    # get post variables (meeting transcript text file and analysis_type)
    # transcript_file = request.files['meeting_transcript']
    transcript_file = request.files.get('meeting_transcript')
    sample_file_name = request.form.get('sample_file')
    analysis_type = request.form['analysis_type']

    if sample_file_name:
        with open(f'Transcripts/{sample_file_name}', 'r') as file:
            transcript_text = file.read()
    else:
        transcript_text = transcript_file.read().decode('utf-8')

    result, analysis_title = post_meeting_analysis(transcript_text, analysis_type)

    return render_template('post-meeting-analysis-result.html', transcript=transcript_text, result=result, analysis_title=analysis_title)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
