import os
import json

from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

ibm_api_key = os.getenv("IBM_API_KEY")
ibm_project_id = os.getenv("IBM_PROJECT_ID")

def get_model():

    model = Model(
        model_id=ModelTypes.LLAMA_3_70B_INSTRUCT,
        params={
            GenParams.MAX_NEW_TOKENS: 900,
            GenParams.RETURN_OPTIONS: {
                'input_text': True,
                'generated_tokens': True,
            },
        },
        credentials=Credentials(
            api_key=ibm_api_key,
            url="https://us-south.ml.cloud.ibm.com",
        ),
        project_id=ibm_project_id,
    )
    return model

model = get_model()

base_prompt_template = \
"""<|system|>
{system_message}

<|user|>
{user_message}

<|assistant|>
"""


class MeetAssistAI:

    @staticmethod
    def extract_markdown_content(string):

        if '```markdown' in string:
            markdown_start = string.find('```markdown') + len('```markdown')
        elif '```' in string:
            markdown_start = string.find('```') + len('```')
        else:
            # No markdown delimiters found, return the original string
            return string

        markdown_end = string.find('```', markdown_start)

        if markdown_end == -1:
            return string[markdown_start:].strip()
        else:
            return string[markdown_start:markdown_end].strip()

    @staticmethod
    def _summarize_meeting_transcript_chunk(meeting_transcript_chunk):
        # meeting_chunk_summarization_prompt_template = \
        system_prompt = """
        You are a smart AI Large Language Model skilled in summarizing text. You are able to read large amounts of texts, extract the most important vital key insights.
        Your task is to summarize the given summary of a  part of meeting transcript (it is incomplete) in a consise and informative manner.
        As the original meeting transcript was very long, it was split into multiple parts and summarized by someone else. You take in one of those summarized parts and summarize it plus extract key insights.
        You should not include any irrelevant information or details that are not important to the main topic of the meeting. You should also not include any personal opinions or comments in your summary. Your summary should be accurate, informative, and easy to understand.
        Make sure the summary does not exceed 2000 words.
        Give your response in markdown format with bullet points to organize the information, as per the following format and don't respond with anything else:
        ```markdown
        * <Key point 1>
        * <Key point 2>
        ...
        ```
        """

        user_prompt = f"""
        Summarize the following part of the meeting transcript, delimitted by tripple single quotes:
        '''
        {meeting_transcript_chunk}
        '''
        """

        prompt = base_prompt_template.format(system_message=system_prompt, user_message=user_prompt)

        generated_response = model.generate(prompt=prompt)
        
        # parse the response
        summary = generated_response['results'][0]['generated_text']
        summary = summary[summary.index('<|assistant|>') + len('<|assistant|>'):]
        summary = summary.strip()
        summary = MeetAssistAI.extract_markdown_content(summary)
        
        return summary

    @staticmethod
    def _summarize_meeting_transcript(meeting_transcript, is_summarized_chunks=False):
        
        if not is_summarized_chunks:
            system_prompt = """

            You are a smart AI Large Language Model skilled in summarizing text. You are able to read large amounts of texts, extract the most important vital key insights, and present them in an easy to read format.
            Your task is to summarize the given meeting transcript in a consise and informative manner. The goal is to have a summary that can serve as a quick review of the meeting for those who attended or as a reference for those who missed the meeting, as such it shouldn't be long.
            You should first read and understand the meeting transcript text carefully and then extract the key points, most important details, and main ideas from the transcript and present them in a clear and organized way. Do not include any irrelevant information, details that are not present in the meeting, or any personal opinions or comments in your summary. 
            Start off the summary by giving a 1 sentence brief overview of what the meeting was about followed by the key points and main ideas discussed during the meeting.
            Give your response in markdown format to organize the information, as per the following format and don't respond with anything else:
            ```markdown
            **Overview: ** <One sentence overview of the meeting>
            
            ## Key Insights:

            ### <Key Topic 1>
            * <Key point 1>
            * <Key point 2>
            ...

            ### <Key Topic 2>
            * <Key point 1>
            * <Key point 2>
            ...

            ...
            ...
            ```
            """
            
            user_prompt = f"""
            Summarize the following meeting transcript, delimitted by tripple single quotes:
            '''
            {meeting_transcript}
            '''
            """

        else:
            system_prompt = \
            """
            You are a smart AI Large Language Model skilled in summarizing text. You are able to read large amounts of texts, extract the most important vital key insights, and present them in an easy to read format.
            Your task is to summarize the given meeting transcript summaries in a consise and informative manner, that is your input will be a bunch of summaries of different chunks of the meeting transcript.
            The goal is to have a summary that can serve as a quick review of the meeting for those who attended or as a reference for those who missed the meeting, as such it shouldn't be long.
            You should first read and understand all the individual meeting summary texts carefully and then extract the key points, most important details, and main ideas from them all and collect, organize and present them in a clear way. Do not include any irrelevant information, details that are not present in the meeting, or any personal opinions or comments in your summary. 
            Start off by giving a 1 sentence brief overview of what the meeting was about followed by the key points and main ideas discussed during the meeting.
            Give your response in markdown format to organize the information, as per the following format and don't respond with anything else:
            ```markdown
            **Overview: ** <One sentence overview of the meeting>
            
            ## Key Insights:

            ### <Key Topic 1>
            * <Key point 1>
            * <Key point 2>
            ...

            ### <Key Topic 2>
            * <Key point 1>
            * <Key point 2>
            ...

            ...
            ...
            ```
            """
            
            user_prompt = f"""
            Summarize the following meeting, delimitted by triple single quotes:
            '''
            {meeting_transcript}
            '''
            """
        
        generated_response = model.generate(prompt=base_prompt_template.format(system_message=system_prompt, user_message=user_prompt))

        # parse the response
        summary = generated_response['results'][0]['generated_text']
        summary = summary[summary.index('<|assistant|>') + len('<|assistant|>'):].strip()
        summary = MeetAssistAI.extract_markdown_content(summary)

        return summary

    @staticmethod
    def get_transcripts():
        transcripts_file = "./Data/transcripts.json"
        with open(transcripts_file, "r") as f:
            transcripts = json.load(f)['transcripts']
        return transcripts

    @staticmethod
    def split_transcript(transcript):
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=3000,
            chunk_overlap=20,
        )
        texts = text_splitter.split_text(transcript)
        return texts
    
    @staticmethod
    def summarize_meeting_transcript(transcript):
        transcript_chunks = MeetAssistAI.split_transcript(transcript)

        if len(transcript_chunks) == 1:
            print("Transcript is small enough to summarize in one go.", flush=True)
            summary = MeetAssistAI._summarize_meeting_transcript(transcript, is_summarized_chunks=False)
        else:
            print(f"Transcript is too large to summarize in one go. Splitting into {len(transcript_chunks)} chunks.", flush=True)
            summaries = []
            for i, chunk in enumerate(transcript_chunks):
                print(f"Summarizing chunk {i + 1}/{len(transcript_chunks)}", flush=True)
                chunk_summary = MeetAssistAI._summarize_meeting_transcript_chunk(chunk)
                print(chunk_summary, "\n\n", flush=True)
                summaries.append(f"Summary for chunk {i + 1}/{len(transcript_chunks)} of the meeting transcript:\n{chunk_summary}")
            summary = MeetAssistAI._summarize_meeting_transcript("\n\n".join(summaries), is_summarized_chunks=True)

        print(f"Summary:\n{summary}", flush=True)
        return summary
    
    @staticmethod
    def _extract_action_items(text, is_transcript=False):

        if is_transcript:
            system_prompt = \
            """
            You are a smart AI Large Language Model skilled in extracting action items from meeting transcript. You are able to read large amounts of meeting transcript texts, identify the most important tasks, and present them in a clear and organized way.
            Your task is to extract the action items from the given meeting transcript. Action items are tasks that need to be completed, assigned, or followed up on after a meeting.
            You should read the meeting transcript carefully and identify all the actionable items mentioned in the text. You should then present them in a clear and organized way, listing each action item, along with optionally the person responsible, the task description, and the due date (if applicable).
            For each action item give a bullet point where the action item is described in one or few sentences, and optionally include the person responsible, the task description, and the due date or duration.
            Give your response in markdown format to organize the information, as per the following format and don't respond with anything else:
            ```markdown
            * <Action item 1>
            * <Action item 2>
            * <Action item 3>
            ...
            ...
            ```
            """

            user_prompt = f"""
            Extract the action items from the following meeting transcript delimitted by triple single quotes:
            '''
            {text}
            '''
            """
        else:  # must be action items extracted from chunks of transcript, need to just combine them simply
            system_prompt = \
            """
            You are a smart AI Large Language Model. Your task is to take in a bunch of action items and give them back in a clear and organized way.
            The action items you will get are from multiple parts of a long meeting. Your goal is to read the given action items text which may be unstructured,
            extract the action items points, and give back a clear and organized list of all the action items.
            Give your response in markdown format to organize the information, as per the following format and don't respond with anything else:
            ```markdown
            * <Action item 1>
            * <Action item 2>
            * <Action item 3>
            ...
            ```
            """

            user_prompt = f"""
            Extract and organize the following action items from different parts of the meeting transcript:
            {text}
            """
        generated_response = model.generate(prompt=base_prompt_template.format(system_message=system_prompt, user_message=user_prompt))

        # parse the response
        action_items = generated_response['results'][0]['generated_text']
        action_items = action_items[action_items.index('<|assistant|>') + len('<|assistant|>'):]
        action_items = action_items.strip()

        return action_items
    
    @staticmethod
    def extract_action_items(transcript):
        transcript_chunks = MeetAssistAI.split_transcript(transcript)

        if len(transcript_chunks) == 1:
            print("Transcript is small enough to extract action items in one go.", flush=True)
            action_items = MeetAssistAI._extract_action_items(transcript)
        else:
            print(f"Transcript is too large to extract action items in one go. Splitting into {len(transcript_chunks)} chunks.", flush=True)
            action_items = []
            for i, chunk in enumerate(transcript_chunks):
                print(f"Extracting action items from chunk {i + 1}/{len(transcript_chunks)}", flush=True)
                chunk_action_items = MeetAssistAI._extract_action_items(chunk, is_transcript=True)
                print(chunk_action_items, "\n\n", flush=True)
                action_items.append(f"Action items from part {i + 1}/{len(transcript_chunks)} of the meeting transcript:\n{chunk_action_items}")
            action_items = MeetAssistAI._extract_action_items("\n\n".join(action_items), is_transcript=False)

        action_items = MeetAssistAI.extract_markdown_content(action_items)
        print(f"Action items:\n{action_items}", flush=True)
        return action_items
    
    @staticmethod
    def _analyze_participants_sentiment(text, is_transcript=False):

        if is_transcript:
            system_prompt = \
            """
            You are a smart AI Large Language Model skilled in analyzing sentiment of text. You are able to read large amounts of texts, identify the sentiments, and present it in a clear and organized way.
            Your task is to analyze the sentiment of the participants in given meeting transcript.
            You should read the meeting transcript carefully and identify the sentiment and overall mood/feelings of the participants during the meeting. You should then present the sentiment in a clear and organized way, describing the overall sentiment of the meeting, and optionally the sentiment of individual participants if applicable.
            The goal is to have a clear understanding of how the participants felt during the meeting, whether they were happy, sad, angry, discontented, or any other emotion, such that future meetings can be improved.
            Give your response in markdown format to organize the information writing the sentiment analysis as a simple markdown text paragraph but with each key word and or phrase like a sentiment, a person, a group, etc. in bold AND underline using double asterisks and <u> (like **<u>this</u>**), as per the following format and don't respond with anything else:
            ```markdown
            <A short summary of the sentiment of the meeting in paragraph form with key words/phrases in bold and underline>
            ```
            """

            user_prompt = f"""
            Analyze the sentiment of the following meeting transcript delimitted by triple single quotes:
            '''
            {text}
            '''
            """
        else:  # must be action items extracted from chunks of transcript, need to just combine them simply
            system_prompt = \
            """
            You are a smart AI Large Language Model. Your task is to take in a bunch of sentiment analysis results and give them back in a clear and organized way.
            The sentiment analysis results you will get are from multiple parts of a long meeting. Your goal is to read the given sentiment analysis results which may be unstructured,
            extract the sentiment analysis points, and give back a clear and organized summary of the sentiment of the meeting. 
            You may choose to edit the sentiment analysis results to make them better as they were extracted from parts of meetings and you need to provide an overall picture.
            Give your response in markdown format to organize the information writing the sentiment analysis as a simple markdown text paragraph but with each key word and or phrase like a sentiment, a person, a group, etc. in bold AND underline using double asterisks and <u> (like **<u>this</u>**), as per the following format and don't respond with anything else:
            ```markdown
            <A short summary of the sentiment of the meeting in paragraph form with key words/phrases in bold and underline>
            ```
            """

            user_prompt = f"""
            Extract and organize the following sentiment analysis results from different parts of the meeting transcript:
            {text}
            """

        generated_response = model.generate(prompt=base_prompt_template.format(system_message=system_prompt, user_message=user_prompt))

        # parse the response
        sentiment_analysis = generated_response['results'][0]['generated_text']
        sentiment_analysis = sentiment_analysis[sentiment_analysis.index('<|assistant|>') + len('<|assistant|>'):]
        sentiment_analysis = sentiment_analysis.strip()

        return sentiment_analysis
    
    @staticmethod
    def analyze_participants_sentiment(transcript):
        transcript_chunks = MeetAssistAI.split_transcript(transcript)

        if len(transcript_chunks) == 1:
            print("Transcript is small enough to analyze sentiment in one go.", flush=True)
            sentiment_analysis = MeetAssistAI._analyze_participants_sentiment(transcript)
        else: 
            print(f"Transcript is too large to analyze sentiment in one go. Splitting into {len(transcript_chunks)} chunks.", flush=True)
            sentiment_analysis = []
            for i, chunk in enumerate(transcript_chunks):
                print(f"Analyzing sentiment from chunk {i + 1}/{len(transcript_chunks)}", flush=True)
                chunk_sentiment_analysis = MeetAssistAI._analyze_participants_sentiment(chunk, is_transcript=True)
                print(chunk_sentiment_analysis, "\n\n", flush=True)
                sentiment_analysis.append(f"Sentiment analysis from part {i + 1}/{len(transcript_chunks)} of the meeting transcript:\n{chunk_sentiment_analysis}")
            sentiment_analysis = MeetAssistAI._analyze_participants_sentiment("\n\n".join(sentiment_analysis), is_transcript=False)

        sentiment_analysis = MeetAssistAI.extract_markdown_content(sentiment_analysis)
        print(f"Sentiment analysis:\n{sentiment_analysis}", flush=True)

        return sentiment_analysis


    @staticmethod
    def _analyze_meeting_productivity(text, is_transcript=False):

        if is_transcript:
            system_prompt = \
            """
            You are a smart AI Large Language Model skilled in analyzing productivity of meetings. You are able to read large amounts of meeting transcript texts, identify the productivity of the meeting, and present it in a clear and organized way.
            Your task is to analyze the productivity of the given meeting transcript.
            You should read the meeting transcript carefully and identify the productivity of the meeting, how productive the meeting was, and what factors contributed to the productivity or lack thereof
            The goal is to have a clear understanding of how productive the meeting was and what factors contributed to the productivity, such that future meetings can be improved.
            Give your response in markdown format, as per the following format and don't respond with anything else:
            ```markdown
            ## Overall Evaluation:
            <Either one of 'Very Productive', 'Somewhat Productive', 'Not Productive'>

            ## Key Factors:
            * <Key factor 1>
            * <Key factor 2>
            ...
            ```
            """

            user_prompt = f"""
            Analyze the productivity of the following meeting transcript delimitted by triple single quotes:
            '''
            {text}
            '''
            """
        else:  # must be action items extracted from chunks of transcript, need to just combine them simply
            system_prompt = \
            """
            You are a smart AI Large Language Model. Your task is to take in a bunch of productivity analysis results and give them back in a clear and organized way.
            The productivity analysis results you will get are from multiple parts of a long meeting. Your goal is to read the given productivity analysis results which may be unstructured,
            extract the productivity analysis points, and give back a clear and organized summary of the productivity of the meeting. 
            You may choose to edit the productivity analysis results to make them better as they were extracted from parts of meetings and you need to provide an overall picture.
            The different parts of the meetings may have different productivity levels and key factors contributing to the productivity, so you need to be smart in creating an overall analysis
            Give your response in markdown format, as per the following format and don't respond with anything else:
            ```markdown
            ## Overall Evaluation:
            <Either one of 'Very Productive', 'Somewhat Productive', 'Not Productive'>

            ## Key Factors:
            * <Key factor 1>
            * <Key factor 2>
            ...
            ```
            """

            user_prompt = f"""
            Extract and organize the following productivity analysis results from different parts of the meeting transcript:
            {text}
            """

        generated_response = model.generate(prompt=base_prompt_template.format(system_message=system_prompt, user_message=user_prompt))

        # parse the response
        productivity_analysis = generated_response['results'][0]['generated_text']
        productivity_analysis = productivity_analysis[productivity_analysis.index('<|assistant|>') + len('<|assistant|>'):]
        productivity_analysis = productivity_analysis.strip()

        return productivity_analysis
    
    @staticmethod
    def analyze_meeting_productivity(transcript):
        transcript_chunks = MeetAssistAI.split_transcript(transcript)

        if len(transcript_chunks) == 1:
            print("Transcript is small enough to analyze productivity in one go.", flush=True)
            productivity_analysis = MeetAssistAI._analyze_meeting_productivity(transcript)
        else:
            print(f"Transcript is too large to analyze productivity in one go. Splitting into {len(transcript_chunks)} chunks.", flush=True)
            productivity_analysis = []
            for i, chunk in enumerate(transcript_chunks):
                print(f"Analyzing productivity from chunk {i + 1}/{len(transcript_chunks)}", flush=True)
                chunk_productivity_analysis = MeetAssistAI._analyze_meeting_productivity(chunk, is_transcript=True)
                print(chunk_productivity_analysis, "\n\n", flush=True)
                productivity_analysis.append(f"Productivity analysis from part {i + 1}/{len(transcript_chunks)} of the meeting transcript:\n{chunk_productivity_analysis}")
            productivity_analysis = MeetAssistAI._analyze_meeting_productivity("\n\n".join(productivity_analysis), is_transcript=False)

        productivity_analysis = MeetAssistAI.extract_markdown_content(productivity_analysis)
        print(f"Productivity analysis:\n{productivity_analysis}", flush=True)

        return productivity_analysis
    

    @staticmethod
    def _suggest_improvements(text, is_transcript=False):

        if is_transcript:
            system_prompt = \
            """
            You are a smart AI skilled in analyzing meeting productivity and suggesting improvements for future ones. You are able to read large amounts of meeting transcript texts, identify the areas of improvement, and present them in a clear and organized way.
            Your task is to review the following meeting transcript and identify specific areas that impact productivity. Some areas of focus include time management, decision-making processes, participant engagement, clarity of communication, and overall effectiveness, but you may identify other areas as well.
            Identify and categorize problems that hinder productivity and provide specific, actionable suggestions for improvement
            The goal is to have a clear understanding of how the meeting can be improved, such that future meetings can be more productive and efficient.
            For each issue, state the issue in one word or a phrase or fewest words possible, and then provide a suggestion or multiple suggestions in one or few sentences.
            Give your response in markdown format, as per the following format and don't respond with anything else:
            ```markdown
            #### 1.  
            **Issue:** <Specific productivity issue in brief> <br>
            **Suggestions:** <Actionable suggestion(s) to address the issue>

            #### 2.
            **Issue:** <Specific productivity issue in brief> <br>
            **Suggestions:** <Actionable suggestion(s) to address the issue>

            ...
            ```
            """

            user_prompt = f"""
            Suggest improvements for the following meeting transcript delimitted by triple single quotes:
            '''
            {text}
            '''
            """

        else:  # must be action items extracted from chunks of transcript, need to just combine them simply
            system_prompt = \
            """
            You are a smart AI Large Language Model. Your task is to take in a bunch of improvement suggestions and give them back in a clear and organized way.
            The improvement suggestions you will get are from multiple parts of a long meeting. Your goal is to read the given improvement suggestions which may be unstructured,
            extract the improvement suggestions points, and give back a clear and organized list of all the improvement suggestions.
            You may choose to edit the improvement suggestions to make them better as they were extracted from parts of meetings and you need to provide an overall picture.
            The goal is to have a clear understanding of how the meeting can be improved, such that future meetings can be more productive and efficient.
            For each issue, state the issue in one word or a phrase or fewest words possible, and then provide a suggestion or multiple suggestions in one or few sentences.
            Give your response in markdown format, as per the following format and don't respond with anything else:
            ```markdown
            #### 1.  
            **Issue:** <Specific productivity issue in brief> <br>
            **Suggestions:** <Actionable suggestion(s) to address the issue>

            #### 2.
            **Issue:** <Specific productivity issue in brief> <br>
            **Suggestions:** <Actionable suggestion(s) to address the issue>

            ...
            ```
            """

            user_prompt = f"""
            Extract and organize the following improvement suggestions from different parts of the meeting transcript:
            {text}
            """

        generated_response = model.generate(prompt=base_prompt_template.format(system_message=system_prompt, user_message=user_prompt))

        # parse the response
        improvement_suggestions = generated_response['results'][0]['generated_text']
        improvement_suggestions = improvement_suggestions[improvement_suggestions.index('<|assistant|>') + len('<|assistant|>'):]
        improvement_suggestions = improvement_suggestions.strip()
        
        return improvement_suggestions
    
    @staticmethod
    def suggest_improvements(transcript):
        transcript_chunks = MeetAssistAI.split_transcript(transcript)

        if len(transcript_chunks) == 1:
            print("Transcript is small enough to suggest improvements in one go.", flush=True)
            improvement_suggestions = MeetAssistAI._suggest_improvements(transcript)
        else:
            print(f"Transcript is too large to suggest improvements in one go. Splitting into {len(transcript_chunks)} chunks.", flush=True)
            improvement_suggestions = []
            for i, chunk in enumerate(transcript_chunks):
                print(f"Suggesting improvements from chunk {i + 1}/{len(transcript_chunks)}", flush=True)
                chunk_improvement_suggestions = MeetAssistAI._suggest_improvements(chunk, is_transcript=True)
                print(chunk_improvement_suggestions, "\n\n", flush=True)
                improvement_suggestions.append(f"Improvement suggestions from part {i + 1}/{len(transcript_chunks)} of the meeting transcript:\n{chunk_improvement_suggestions}")

            improvement_suggestions = MeetAssistAI._suggest_improvements("\n\n".join(improvement_suggestions), is_transcript=False)

        improvement_suggestions = MeetAssistAI.extract_markdown_content(improvement_suggestions)
        print(f"Improvement suggestions:\n{improvement_suggestions}", flush=True)

        return improvement_suggestions
    

    @staticmethod
    def generate_agenda(meeting_topic, meeting_background, meeting_participants):
        system_prompt = \
        """
        You are a smart AI Large Language Model skilled in creating meeting agendas. You are able to create a structured agenda for a meeting, given the meeting topic, background information, and list of participants.
        Your task is to create an agenda for an upcoming meeting. The agenda should be organized in sections.
        Sections may include:
        - Goals and Objectives: List the goals and objectives of the meeting, each in a one or few words.
        - Discussion Topics: List the topics that will be discussed during the meeting, each in a one or few words.
        - Preparation Required: List any preparation action items that need to be completed before the meeting for the participants.
        - Expected Outcomes: List the expected outcomes of the meeting, each in a one or few words.
        - Any other relevant sections that you think are important.

        You may leave out any of the sections suggested if not applicable and add your own ones if valuable. The goal of the agenda is to provide a clear structure for the meeting and ensure that all participants are prepared and know what to expect, to ensure optimal meeting productivity.
        Give your response in markdown format to organize the information, as per the following format and don't respond with anything else:
        - 
        ```markdown
        ## Agenda for the "<Meeting Topic>" Meeting

        ### Goals and Objectives
        * <Goal 1>
        * <Goal 2>
        ...

        ### Discussion Topics
        * <Topic 1>
        * <Topic 2>
        ...

        ### Preparation Required
        * <Preparation action item 1>
        * <Preparation action item 2>

        <any other relevant sections>
        ...
        ```
        """

        user_prompt = f"""
        Create an agenda for the meeting with following details:
        - Meeting Topic: {meeting_topic}
        - Meeting Background: {meeting_background}
        - Meeting Participants: {meeting_participants}
        """

        generated_response = model.generate(prompt=base_prompt_template.format(system_message=system_prompt, user_message=user_prompt))

        # parse the response
        agenda = generated_response['results'][0]['generated_text']
        agenda = agenda[agenda.index('<|assistant|>') + len('<|assistant|>'):]
        agenda = agenda.strip()
        agenda = MeetAssistAI.extract_markdown_content(agenda)

        return agenda
    