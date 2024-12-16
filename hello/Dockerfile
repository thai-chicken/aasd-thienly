FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install spade reportlab pydantic xhtml2pdf markdown2

ENV PYTHONPATH "${PYTHONPATH}:/app"

# RUN chmod +x src/main.py
# CMD python -u src/main.py

CMD ["bash"]