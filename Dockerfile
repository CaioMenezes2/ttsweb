# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies and voice packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    espeak \
    libespeak1 \
    espeak-data \
    speech-dispatcher \
    speech-dispatcher-espeak \
    ffmpeg \
    locales \
    wget \
    unzip \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8

# Install Microsoft Speech Platform
RUN wget -q https://download.microsoft.com/download/A/6/4/A64012D6-D56F-4E58-85E3-531E56ABC0E6/x64/SpeechPlatformRuntime/SpeechPlatformRuntime.msi && \
    wget -q https://download.microsoft.com/download/4/0/D/40D6347A-AFA5-417D-A9BB-173D937BEED4/MSSpeech_TTS_en-US_ZiraPro.msi && \
    apt-get update && \
    apt-get install -y wine64 && \
    wine msiexec /i SpeechPlatformRuntime.msi /qn && \
    wine msiexec /i MSSpeech_TTS_en-US_ZiraPro.msi /qn && \
    rm *.msi && \
    apt-get remove -y wine64 && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables for locale
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]