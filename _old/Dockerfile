from python:3.10
ENV dtw="/root/github.com/loicbourgois/downtowhat"
COPY requirements.txt $dtw/requirements.txt
RUN python -m pip install -r $dtw/requirements.txt
COPY main.py $dtw/main.py
COPY common.py $dtw/common.py
COPY data_builders $dtw/data_builders
CMD cd $dtw/.. && PYTHONPATH=$dtw python -m downtowhat.main
