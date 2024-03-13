FROM python:3.9

RUN apt-get update -y 

RUN mkdir -p /usr/local/tmp 

COPY requirements.txt /usr/local/tmp/

RUN pip install -r /usr/local/tmp/requirements.txt \
	&& rm -fr /usr/local/tmp

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD ["main.py", "--server.port=8501"]
