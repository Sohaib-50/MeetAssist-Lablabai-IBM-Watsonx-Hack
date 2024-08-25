FROM python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
<<<<<<< HEAD
EXPOSE 5000
=======
EXPOSE 10000
>>>>>>> 4dc9f61 (mvp)
CMD ["python", "app.py"]
