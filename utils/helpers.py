<<<<<<< HEAD
def get_welcome_message():
    return "Welcome to MeetAssist, your solution for efficient meetings!"
=======
import markdown
from textwrap import dedent
from utils.ai import MeetAssistAI

def get_welcome_message():
    return "Welcome to MeetAssist, your solution for efficient meetings!"


def pre_meeting_analysis(meeting_topic, meeting_background, meeting_participants):
    result = MeetAssistAI.generate_agenda(meeting_topic, meeting_background, meeting_participants)
    result = markdown.markdown(dedent(result.strip()), extensions=['fenced_code'])

    return result


def post_meeting_analysis(transcript, analysis_type):

    if analysis_type == "summary":
        result = MeetAssistAI.summarize_meeting_transcript(transcript)
        analysis_title = "Meeting Summary"
    elif analysis_type == "action_items":
        result = MeetAssistAI.extract_action_items(transcript)
        analysis_title = "Action Items"
    elif analysis_type == "sentiment_analysis":
        result = MeetAssistAI.analyze_participants_sentiment(transcript)
        analysis_title = "Participants' Sentiment Analysis"
    elif analysis_type == "productivity_analysis":
        result = MeetAssistAI.analyze_meeting_productivity(transcript)
        analysis_title = "Productivity Analysis"
    elif analysis_type == "improvement_suggestions":
        result = MeetAssistAI.suggest_improvements(transcript)
        analysis_title = "Improvement Suggestions"

    # # mock response for testing
    # return """<p><strong>Overview:</strong> The meeting discusses the design of a remote control for a television set, covering its functionality, usability, and market requirements.</p>
    #     <h2>Key Insights</h2>
    #     <h3>Remote Control Design</h3>
    #     <ul>
    #     <li>The remote control should be small, inexpensive, and have a single battery and minimal buttons.</li>
    #     <li>A menu button is suggested to access different functions on the television.</li>
    #     <li>The possibility of making the remote control compatible with other televisions is discussed.</li>
    #     </ul>
    #     <h3>User Interface and Functionality</h3>
    #     <ul>
    #     <li>The remote control should be able to influence the television set, including audio and video, in a cordless way.</li>
    #     <li>Basic operations such as on/off, channel switching, and teletext are mentioned.</li>
    #     </ul>
    #     <h3>Market Research and Target Groups</h3>
    #     <ul>
    #     <li>Users dislike the look and feel of current remote controls, find them hard to use, and have frustrations with zapping.</li>
    #     <li>Two target groups are identified: younger users (16-45) who are interested in new features and critical of their spending, and older users (46-65) who are less interested in new features but spend their money more easily.</li>
    #     </ul>
    #     <h3>Product Requirements</h3>
    #     <ul>
    #     <li>The remote control should have a power button, channel selection, volume control, and a menu.</li>
    #     <li>The use of an LCD screen and the importance of design are considered.</li>
    #     </ul>""", analysis_title


    # Convert the result to HTML
    result = markdown.markdown(dedent(result.strip()), extensions=['fenced_code'])

    print(f"HTML-ized result: {result}", flush=True)

    return result, analysis_title
>>>>>>> 4dc9f61 (mvp)
