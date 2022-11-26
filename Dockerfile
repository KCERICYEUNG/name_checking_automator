FROM debian

WORKDIR /app

COPY main.py .
COPY requirement.txt .

RUN pip install -r requirement.txt

CMD ["streamlit","run","main.py"]