from flask import Flask, render_template
from utils.helpers import get_welcome_message

app = Flask(__name__)

@app.route('/')
def home():
    welcome_message = get_welcome_message()
    return render_template('index.html', message=welcome_message)

if __name__ == '__main__':
    app.run(debug=True)
