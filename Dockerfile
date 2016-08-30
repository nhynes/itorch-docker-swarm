FROM jupyterhub/jupyterhub

MAINTAINER Nick Hynes <nhynes@mit.edu>

RUN pip install --upgrade pip
RUN pip install docker-py==1.9.0
RUN pip install git+git://github.com/jupyter/dockerspawner.git

COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
COPY sesameauthenticator.py /srv/jupyterhub_config/sesameauthenticator.py

RUN mkdir /srv/users

# expose hub api and porxy
EXPOSE 8080
EXPOSE 8001

# tell dockerspawner where to look for the docker engine
ENV DOCKER_HOST https://swarm:2375

ENTRYPOINT ["jupyterhub", "-f", "/srv/jupyterhub_config/jupyterhub_config.py"]
