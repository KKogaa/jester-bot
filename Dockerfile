FROM python:3.11.1-slim

RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y
RUN apt-get install -y ffmpeg git curl

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv --copies $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . /opt/jester-project
WORKDIR /opt/jester-project
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["python3", "discord.py"]