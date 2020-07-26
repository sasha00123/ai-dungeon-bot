FROM python:3

RUN pip install --upgrade pip poetry setuptools wheel

COPY . .

RUN python3 -m venv /env && . /env/bin/activate && poetry install


WORKDIR src/ai_dungeon

EXPOSE 80
CMD ["/env/bin/python3", "main.py"]