FROM python:3.7-slim
RUN apt-get update && \
    apt-get install -y \
    libpng-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    gfortran \
    gcc musl-dev python3-pip libgl1 libgl1-mesa-glx libglib2.0-0 libgirepository-1.0-1

RUN pip install -U pip
RUN pip install --no-cache-dir numpy~=1.20 flask pillow~=7.2.0
# RUN pip install --no-cache-dir mscviplib==2.200731.16

RUN apt-get install git -y

RUN git clone https://github.com/ultralytics/yolov5  # clone
RUN pip install -r yolov5/requirements.txt 
RUN pip install yolov5

COPY app /app


# Expose the port
EXPOSE 80

# Set the working directory
WORKDIR /app

# Run the flask server for the endpoints
CMD python -u app.py --model yolov5_custom