# FROM debian
#
# WORKDIR /app
#
# COPY main.py .
# COPY requirement.txt .
#
# RUN pip install -r requirement.txt
#
# CMD ["streamlit","run","main.py"]
FROM python:3.9-bullseye
#Expose port 8080
EXPOSE 8080

#Optional - install git to fetch packages directly from github
RUN apt-get update && apt-get install -y git
Run wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
Run apt-get install -y ./google-chrome-stable_current_amd64.deb
Run apt-get install -y libglib2.0 libnss3 libgconf-2-4 libfontconfig1

#Copy Requirements.txt file into app directory
COPY requirement.txt app/requirement.txt

#install all requirements in requirements.txt
RUN pip install -r app/requirement.txt

#Copy all files in current directory into app directory
COPY . /

#Change Working Directory to app directory
WORKDIR /

#Run the application on port 8080
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0"]