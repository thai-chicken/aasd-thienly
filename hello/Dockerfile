FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install spade==3.3.3 reportlab pydantic xhtml2pdf markdown2

ENV PYTHONPATH="/app"

# RUN chmod +x src/main.py
# CMD python -u src/main.py

CMD ["bash"]