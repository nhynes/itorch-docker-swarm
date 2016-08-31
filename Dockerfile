FROM jupyterhub/jupyterhub

MAINTAINER Nick Hynes <nhynes@mit.edu>

RUN pip install --upgrade pip
RUN pip install \
    docker-py==1.9.0 \
    git+git://github.com/jupyter/dockerspawner.git \
    jupyter_client

# expose hub service, proxy, and api, respectively
EXPOSE 8080
EXPOSE 8000
EXPOSE 8081

COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
COPY sesameauthenticator.py /srv/jupyterhub/sesameauthenticator.py

ENTRYPOINT ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]
