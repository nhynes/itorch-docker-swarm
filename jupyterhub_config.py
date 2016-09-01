import os
import sys
sys.path.insert(0, '/srv/jupyterhub')

# Configuration file for Jupyter Hub
c = get_config()

c.JupyterHub.log_level = "INFO"

c.JupyterHub.confirm_no_ssl = True

# need to listen on all ifaces because it's running in a container
# requires setting HUB_IP via env vars
c.JupyterHub.proxy_api_ip = '0.0.0.0'
c.JupyterHub.hub_ip = '0.0.0.0'

# Authenticator
c.JupyterHub.authenticator_class = 'sesameauthenticator.SesameAuthenticator'
c.LocalAuthenticator.create_system_users = True
c.JupyterHub.admin_access = True
c.Authenticator.whitelist = set()
c.Authenticator.admin_users = {'nhynes'}

# Spawner
hub_ip = os.environ['HUB_IP']
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.container_image = 'quay.io/nhynes/itorch-singleuser'
c.DockerSpawner.container_ip = '0.0.0.0'
c.DockerSpawner.remove_containers = True
c.DockerSpawner.hub_ip_connect = hub_ip
c.DockerSpawner.extra_create_kwargs.update({
    'command': '/usr/local/bin/start-singleuser.sh --kernel=itorch'
})
os.environ['DOCKER_HOST'] = hub_ip + ':3376' # one server to rule them all

# Jupyterhub params that can also be set in /etc/ipython but maybe not because itorch
#c.Spawner.notebook_dir = '~/notebooks'
#c.Spawner.args = ['--NotebookApp.default_url=/notebooks/Welcome.ipynb']
