

import requests

api_key = "xwtmg9hqL5KvpdmL17HlYYi5tItR6njRjlqA7rYqocWS"
# curl -X POST 'https://iam.cloud.ibm.com/identity/token' -H 'Content-Type: application/x-www-form-urlencoded' -d 'grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=xwtmg9hqL5KvpdmL17HlYYi5tItR6njRjlqA7rYqocWS'

access_token = "eyJraWQiOiIyMDI0MDgwMzA4NDEiLCJhbGciOiJSUzI1NiJ9.eyJpYW1faWQiOiJJQk1pZC02OTIwMDBJT1AyIiwiaWQiOiJJQk1pZC02OTIwMDBJT1AyIiwicmVhbG1pZCI6IklCTWlkIiwianRpIjoiZmE5MzQ4YjMtMTc0MC00MmNkLWIwMGUtODgyNjZkZTE5Njg0IiwiaWRlbnRpZmllciI6IjY5MjAwMElPUDIiLCJnaXZlbl9uYW1lIjoiU29oYWliIiwiZmFtaWx5X25hbWUiOiJBYmJhc2kiLCJuYW1lIjoiU29oYWliIEFiYmFzaSIsImVtYWlsIjoic29oYWliYWhtZWRhYmJhc2kyQGdtYWlsLmNvbSIsInN1YiI6InNvaGFpYmFobWVkYWJiYXNpMkBnbWFpbC5jb20iLCJhdXRobiI6eyJzdWIiOiJzb2hhaWJhaG1lZGFiYmFzaTJAZ21haWwuY29tIiwiaWFtX2lkIjoiSUJNaWQtNjkyMDAwSU9QMiIsIm5hbWUiOiJTb2hhaWIgQWJiYXNpIiwiZ2l2ZW5fbmFtZSI6IlNvaGFpYiIsImZhbWlseV9uYW1lIjoiQWJiYXNpIiwiZW1haWwiOiJzb2hhaWJhaG1lZGFiYmFzaTJAZ21haWwuY29tIn0sImFjY291bnQiOnsidmFsaWQiOnRydWUsImJzcyI6IjA3ZmUyZmY1ZjNkNzQ2MGRhYmIwZjk3YWVlZTNjMDA4IiwiaW1zX3VzZXJfaWQiOiIxMjYyNTUxNSIsImZyb3plbiI6dHJ1ZSwiaW1zIjoiMjc0NDExNiJ9LCJpYXQiOjE3MjQ0NzMxNDQsImV4cCI6MTcyNDQ3Njc0NCwiaXNzIjoiaHR0cHM6Ly9pYW0uY2xvdWQuaWJtLmNvbS9pZGVudGl0eSIsImdyYW50X3R5cGUiOiJ1cm46aWJtOnBhcmFtczpvYXV0aDpncmFudC10eXBlOmFwaWtleSIsInNjb3BlIjoiaWJtIG9wZW5pZCIsImNsaWVudF9pZCI6ImRlZmF1bHQiLCJhY3IiOjEsImFtciI6WyJwd2QiXX0.RdIrKmQzmXne0-vbR_3Fk3TUovc5_HGLILc3M3M5P_TFmt11X5MvTpDWuMHCfZ28rLLU9EpYlqpXDxj-Fo9Sae-2Jso8pJwFUb-4zYRLlg-JVe15BmF1jqwAf1-vaHywgnSh4PGfsAf1zVLWxUHBFG6Z8hXBubVDfa5FpuvykREKB5GiNSVxsfXf01mqD7ldYeZ0lDfGp9eA9unkj5mU_4IqwjzPjCRwAARrL_fHKHnKwQX5ILWk5Y1gnqWvFvXBfFBLoD5RM5UaOtsdzB_jI4TsKZorWA2bBaRCNvLFEtgtyY8f8kzPnO9uigFfvGbJPb4RsaJ7DWT0D3KC7-KTjA"
url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

body = {
	"input": """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You always answer the questions with markdown formatting using GitHub syntax. The markdown formatting you support: headings, bold, italic, links, tables, lists, code blocks, and blockquotes. You must omit that you answer the questions with markdown.

Any HTML tags must be wrapped in block quotes, for example ```<html>```. You will be penalized for not rendering code in block quotes.

When returning code blocks, specify language.

You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. 
Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don'\''t know the answer to a question, please don'\''t share false information.<|eot_id|><|start_header_id|>user<|end_header_id|>

hi<|eot_id|><|start_header_id|>assistant<|end_header_id|>

**Hello!** I'\''m happy to assist you with any questions or topics you'\''d like to discuss. How can I help you today?<|eot_id|><|start_header_id|>user<|end_header_id|>

come up with 3 ideas for a hackathon projects. Just give idea titles in a list.?<|eot_id|><|start_header_id|>assistant<|end_header_id|>
""",
	"parameters": {
		"decoding_method": "greedy",
		"max_new_tokens": 900,
		"repetition_penalty": 1
	},
	"model_id": "meta-llama/llama-3-8b-instruct",
	"project_id": "b29a2af9-5d63-4a6f-a179-4b739dac03cd"
}

headers = {
	"Accept": "application/json",
	"Content-Type": "application/json",
	"Authorization": f"Bearer {access_token}"
}

response = requests.post(
	url,
	headers=headers,
	json=body
)

if response.status_code != 200:
	raise Exception("Non-200 response: " + str(response.text))

data = response.json()
print(data["results"][0]["generated_text"])