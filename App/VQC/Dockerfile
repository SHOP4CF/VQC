#Wybieramy fundament naszej apki
FROM ubuntu:20.04

# -y is needed so that every asnwer during installation is yes
RUN apt-get update && apt-get install -y \
    python3.8 \
    pip

RUN apt-get update --fix-missing
#those two are needed for cv2 to be working
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements.txt .

RUN pip install -r requirements.txt
#this is needed to connect with Atlas problably in developement we won't need it
# RUN pip install pymongo[srv]

WORKDIR /app
#This will create environmental variable in our Ubuntu system within DockerImage
ENV PYTHONPATH=/app 

COPY app ./app

CMD ["waitress-serve", "--listen=0.0.0.0:5000", "--call", "app:create_app"]