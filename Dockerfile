# docker run \
#     -p 8080:8080 -p 8081:8081 -p 80:8000 \
#     -e "HUB_IP=$(ip -o -4 a show eth0 | awk '{print $4}' | sed 's/\/[0-9]\+$//')" \
#     -e "OPEN_SESAME=$SECRET"
#     nhynes/jupyterhub

FROM jupyterhub/jupyterhub

MAINTAINER Nick Hynes <nhynes@mit.edu>

RUN pip install --upgrade pip
RUN pip install docker-py==1.9.0
RUN pip install git+git://github.com/jupyter/dockerspawner.git

# expose hub service, proxy, and api, respectively
EXPOSE 8080
EXPOSE 8000
EXPOSE 8081

COPY sesameauthenticator.py /srv/jupyterhub/sesameauthenticator.py
COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py

ENTRYPOINT ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]
