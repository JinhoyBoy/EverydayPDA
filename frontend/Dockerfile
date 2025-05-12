FROM python:3.11

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg and flac
RUN apt-get update && apt-get install -y ffmpeg
RUN apt-get install -y flac


# Copy bot files
COPY . .

# Run the bot
CMD ["python", "main.py"]