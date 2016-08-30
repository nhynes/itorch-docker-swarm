import os

# Configuration file for Jupyter Hub
c = get_config()

c.JupyterHub.log_level = "INFO"

c.JupyterHub.confirm_no_ssl = True

# Authenticator
c.JupyterHub.authenticator_class = 'sesameauthenticator.SesameAuthenticator'
c.JupyterHub.create_system_users = True
c.JupyterHub.admin_access = True
c.Authenticator.whitelist = set()
c.Authenticator.admin_users = {'nhynes'}

# Spawner
c.JupyterHub.spawner_class = 'dockerspawner.SystemUserSpawner'
c.DockerSpawner.container_image = 'dhunter/itorch-notebook'
c.DockerSpawner.container_ip = '0.0.0.0'
c.DockerSpawner.remove_containers = True
c.DockerSpawner.volumes = {'/var/run/restuser':'/var/run/restuser.sock'}

# The docker instances need access to the Hub, so the default loopback port
# doesn't work. We need to tell the hub to listen on 0.0.0.0 because it's in a
# container, and we'll expose the port properly when the container is run. Then,
# we explicitly tell the spawned containers to connect to the proper IP address.
c.JupyterHub.proxy_api_ip = '0.0.0.0'
c.JupyterHub.hub_ip = '0.0.0.0'
c.DockerSpawner.hub_ip_connect = os.environ['HUB_IP']

c.Spawner.notebook_dir = '~/notebooks'
c.Spawner.args = ['--NotebookApp.default_url=/notebooks/Welcome.ipynb']
