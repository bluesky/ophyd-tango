FROM condaforge/miniforge3:latest

RUN conda create -yn pytango -c tango-controls python=3.7 pytango ipython
RUN conda run -n pytango python -m pip install ophyd bluesky 

ENV TANGO_HOST=tango-cs:10000

RUN apt-get update && apt-get install -y netcat

COPY ophyd_tango.py .

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "pytango", "ipython", "-i", "ophyd_tango.py"]
