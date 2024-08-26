
import markdown
from textwrap import dedent
from utils.ai import MeetAssistAI

def get_welcome_message():
    return "Welcome to MeetAssist, your solution for efficient meetings!"


def pre_meeting_analysis(meeting_topic, meeting_background, meeting_participants):
    try:
        result = MeetAssistAI.generate_agenda(meeting_topic, meeting_background, meeting_participants)
    except:
        # error message markdown result
        result = """
        ### Oops!
        An error occurred while generating the meeting agenda, sorry!
        Please go back and try once more.
        """
    result = markdown.markdown(dedent(result.strip()), extensions=['fenced_code'])

    return result


def post_meeting_analysis(transcript, analysis_type):

    try:
        if analysis_type == "summary":
            analysis_title = "Meeting Summary"
            result = MeetAssistAI.summarize_meeting_transcript(transcript)
        elif analysis_type == "action_items":
            analysis_title = "Action Items"
            result = MeetAssistAI.extract_action_items(transcript)
        elif analysis_type == "sentiment_analysis":
            analysis_title = "Participants' Sentiment Analysis"
            result = MeetAssistAI.analyze_participants_sentiment(transcript)
        elif analysis_type == "productivity_analysis":
            analysis_title = "Productivity Analysis"
            result = MeetAssistAI.analyze_meeting_productivity(transcript)
        elif analysis_type == "improvement_suggestions":
            analysis_title = "Improvement Suggestions"
            result = MeetAssistAI.suggest_improvements(transcript)
    except:
        # error message markdown result
        result = """
        ### Oops!
        An error occurred while generating the analysis, sorry!
        Please go back and try once more.
        """

    # Convert the result to HTML
    result = markdown.markdown(dedent(result.strip()), extensions=['fenced_code'])

    print(f"HTML-ized result: {result}", flush=True)

    return result, analysis_title