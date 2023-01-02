## Docker description
### Images
Quick description of our Dockerfile:
`FROM ubuntu:20.04` - we load our base image on which everything will run, there are quite a lot to choose for me it could be Ubuntu:version or python:version that is preinstalled with Debian. This choice has big influence on final size of the image.
* [Quick story about why selecting proper image may be crucial](https://www.innoq.com/en/blog/choose-your-docker-base-image-wisely/)
* [Why not to use Alpine image for Python projects](https://pythonspeed.com/articles/alpine-docker-python/)
* [Quick tutorial helping which one to choose](https://pythonspeed.com/articles/base-image-python-docker-images/)
* [Speed comparison of Ubuntu and Debian based images](https://pythonspeed.com/articles/faster-python/)
* DockerHub: [Ubuntu](https://hub.docker.com/_/ubuntu) or [Debian](https://hub.docker.com/_/python)


`RUN apt-get update && apt-get install -y \ python3.8 \ pip` - if we choose just OS as our base we need to install python by ouselves

`RUN apt-get install ffmpeg libsm6 libxext6  -y` This is mandatory for open CV to be working. [Source](https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo)
* [Best practices of writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
* [Short article about real size of Docker Images](https://semaphoreci.com/blog/2018/03/14/docker-image-size.html)

`docker image` command to play with created images `docker history image_name` shows all layers and their sizes

### Networks
There are quite a few choices to make with [networks](https://docs.docker.com/network/) in our usecase we could either use [bridge network](https://docs.docker.com/network/bridge/) so that containers in one bridge can communicate with one another or [host network](https://docs.docker.com/network/network-tutorial-host/) to bind container directly to the host. For maintaining network there is a `docker network` command with short [tutorial](https://docs.docker.com/engine/tutorials/networkingcontainers/). During running containers in bridge mode we can map them to [different ports](https://docs.docker.com/config/containers/container-networking/) on the host machine

### Storage
* [Introduction to data storage in Docker](https://docs.docker.com/storage/)
* [Bind mounts](https://docs.docker.com/storage/bind-mounts/)
* [Volumes](https://docs.docker.com/storage/volumes/) 
* When we've already created a container we can easily run it to see its filesystem, it may be very useful for debugging. We can do it using `docker exec -t -i mycontainer /bin/bash`
### Running container
We can use `docker run command` but if we have a lot of port binding, bind mounts etc. this command may become quite messy so what we can use is [docker-compose](https://docs.docker.com/compose/)

### Tests
To perform tests just go to `VQC` folder and run `pytest` if you don't want to test stuff connected with db run `pytest -m "not db"`. If you want to see how much of your code is being tested you can use `coverage` module. Run `coverage run -m pytest` and it willcrate .coverage file for you. Then you can run `coverage report` to see report in CLI or `coverage html` that generates files in the htmlcov directory. Open htmlcov/index.html in your browser to see the report.

### Profiling
If you want to profile entire app you have to uncomment this line: `app = ProfilerMiddleware(app, profile_dir='.')` in `VQC/vqc/__init__.py` then run everything as it is descripted above but instead of running app as docker container run it normally in your terminal with: `waitress-serve --listen=127.0.0.1:5000 --call vqc:create_app`. Then just run everything and after stopping inside `profiling directory` you should see created files then just run `snakeviz profiling` and html page will be opened where you can choose different requests.