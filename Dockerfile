# Use Windows Server Core as base image
FROM mcr.microsoft.com/windows/servercore:ltsc2019

# Set PowerShell as the default shell
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Download and install Python 3.9
RUN Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe" -OutFile "python-3.9.7.exe" ; \
    Start-Process python-3.9.7.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; \
    Remove-Item -Force python-3.9.7.exe

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR C:\app

# Copy project files
COPY . C:\app\

# Install Python dependencies
RUN python -m pip install --upgrade pip ; \
    pip install --no-cache-dir -r requirements.txt

# Make port 8000 available
EXPOSE 8000

# Run the application
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "app:app"]