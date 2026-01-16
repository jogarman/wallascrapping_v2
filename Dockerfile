# Use the official Apify Python Selenium image
# It comes with Python 3.11, Chrome, and Selenium/Webdriver pre-installed
FROM apify/actor-python-selenium:3.11

# Set the working directory
WORKDIR /usr/src/app

# Copy dependency definition
# We use requirements.txt for simplicity in this container
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV USE_STD_DRIVER=true 
# We force standard driver because Apify image provides a tuned Chrome+Driver 
# that works better than undetected-chromedriver in this specific container.
# However, if detection is an issue, we can toggle this back.

# Run the orchestrator
CMD ["python", "-m", "src.main"]
