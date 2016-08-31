from jupyter_client.localinterfaces import public_ips
import os
import sys
sys.path.insert(0, '/srv/jupyterhub')

# Configuration file for Jupyter Hub
c = get_config()

c.JupyterHub.log_level = "INFO"

c.JupyterHub.confirm_no_ssl = True

# need to listen on all ifaces because it's running in a container
# requires setting HUB_IP and DOCKER_HOST via env vars
c.JupyterHub.proxy_api_ip = '0.0.0.0'
c.JupyterHub.hub_ip = public_ips()[0]

# Authenticator
c.JupyterHub.authenticator_class = 'sesameauthenticator.SesameAuthenticator'
c.LocalAuthenticator.create_system_users = True
c.JupyterHub.admin_access = True
c.Authenticator.whitelist = set()
c.Authenticator.admin_users = {'nhynes'}

# Spawner
c.JupyterHub.spawner_class = 'dockerspawner.SystemUserSpawner'
c.DockerSpawner.container_image = 'dhunter/itorch-notebook'
c.DockerSpawner.container_ip = '0.0.0.0'
c.DockerSpawner.remove_containers = True
c.DockerSpawner.hub_ip_connect = c.JupyterHub.hub_ip
os.environ['DOCKER_HOST'] = c.JupyterHub.hub_ip # one server to rule them all
#c.DockerSpawner.volumes = {'/var/run/restuser':'/var/run/restuser.sock'}

# Jupyterhub params that can also be set in /etc/ipython but maybe not because itorch
c.Spawner.notebook_dir = '~/notebooks'
c.Spawner.args = ['--NotebookApp.default_url=/notebooks/Welcome.ipynb']
