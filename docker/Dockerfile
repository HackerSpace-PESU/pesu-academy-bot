# Set base image as Ubuntu 20.04
FROM ubuntu:20.04

# Install python3 and pip3
RUN apt update -y
RUN apt upgrade -y
RUN apt install python3 python3-pip -y && pip3 install --upgrade pip
RUN echo "Python version: $(python3 --version)"
RUN echo "pip version: $(pip3 --version)"

# Install Chrome
ARG DEBIAN_FRONTEND=noninteractive
RUN apt install vim wget dpkg unzip tzdata -y
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install ./google-chrome-stable_current_amd64.deb -y
RUN rm ./google-chrome-stable_current_amd64.deb
RUN echo "Chrome version: $(google-chrome --version) installed at $(which google-chrome)"

# Install Chromedriver
RUN wget https://chromedriver.storage.googleapis.com/98.0.4758.102/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
RUN rm chromedriver_linux64.zip
RUN echo "Chromedriver version: $(chromedriver --version) installed at $(which chromedriver)"

# Setting up Python environment
COPY ../src/ src/
COPY ../data/ data/
COPY ../.env .env
COPY ../start.sh start.sh
RUN apt install git libpq-dev python3-dev -y
RUN git config --global user.email "emailaddress@domain.com"
RUN git config --global user.name "Your Name"
COPY ../requirements.txt requirements.txt
RUN pip3 install --no-deps -r requirements.txt
RUN python3 -c "import nltk; nltk.download('wordnet')"

# Running the bot
CMD ["python3", "src/bot.py"]