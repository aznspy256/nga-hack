# flaskTunnel
_A Proxy Tunnel Relay using Flask on Alpine & Gunicorn inside Docker_  
**by [Collective Acuity](https://collectiveacuity.com)**

## Components
- Alpine Edge (OS)
- Python 3.5.1 (Environment)
- Gunicorn 19.4.5 (Server)
- Flask 0.10.1 (Framework)
- Gevent 1.1.2 (Thread Manager)
- NodeJS 4.3.0 (Environment)
- LocalTunnel 1.8.1 (Proxy Service)

## Dev Env
- Docker (Provisioning)
- BitBucket (Version Control)
- PyCharm (IDE)
- Dropbox (Sync, Backup)

## Languages
- Python 3.5
- Shell Script

## Features
- Local Tunnel Enabled
- Flask in a Container
- OAuth Collection Endpoints
- Local Credential Controls
- Lean Footprint

## Setup DevEnv
1. Install Docker Toolbox on Local Device
2. Install Git on Local Device
3. Clone/Fork Repository from Version Control service
4. Create a /cred Folder in Root to Store Tokens
5. **[Optional]** Create a New Private Remote Repository

## Scheduler Sub-Folders 
-- _models/_ (sub-folder for data object model declarations)  
-- _static/_ (sub-folder for public accessible application content)  
-- _templates/_ (sub-folder for html templates)  

## Configuration Settings
flaskTunnel requires certain configuration settings in order to properly relay a request to another server and to authorize the tunnel to be opened and closed remotely. The following environmental variables should be passed in at startup with the correct variables:

- system_ip_address: '127.0.0.1'
- server_system_port: 5000
- tunnel_flask_token: 'abcdefgh01234456789_IJKLMNOPQrstuv-wxyz'
- tunnel_system_port: 5002 **optional**
- tunnel_container_port: 0 **optional**
- tunnel_subdomain_name: 'somerandomstringoflowercaseletters' **optional**

flaskTunnel is designed to look for these settings first in environmental variables, then in a file called cred/tunnel.yaml. A copy of tunnel.yaml can be found in the notes folder and can be copied to the cred/ folder for local development and testing. If you are using the pocketLab management tool, it will automatically add any values to the environmental variables which are declared in cred/tunnel.yaml when starting the service in a docker container and will match the tunnel_container_port to whichever port is mapped to the gunicorn start command in lab.yaml.

**OAuth Button**
A copy of oauth.yaml is also provided in the notes folder to be used as a template for local development and testing of different oauth2 clients. Any file in the cred folder which contains the same variables as the oauth.yaml file will be added to the list of oauth2 authorization services which can be accessed through a link on the dashboard. Selection of the service can be toggled by adding the query field ?oauth=title_of_file_without_yaml to the landing page. If no files are found, the link to OAuth authorization is disabled.

## Launch Commands
**start.sh**  
_Creates container with required volumes and starts flask on a gunicorn server_  
Requires:  

- Container Alias
- Container Ports
- Mapped Volumes
- Initial Command
- Container Root Folder Name (if AWS EC2 deployment with awsDocker module)
- Virtualbox Name (if Windows or Mac localhost)

**rebuild.sh**  
_Initiates an automated build command on Docker to update base image_  
Requires:  

- Container Alias
- Token from Docker Build Settings
- Environment Variable File (in cred/docker.yaml)

**tunnel.sh**  
_Initiates a secure tunnel from local device to endpoint on localtunnel.me_  
Requires:  

- Container Alias

## Collaboration Notes
_The Git and Docker repos contain all the configuration information required for collaboration except access tokens. To synchronize access tokens across multiple devices, platforms and users without losing local control, you can use LastPass, an encrypted email platform such as ProtonMail or smoke signals. If you use any AWS services, use AWS IAM to assign user permissions and create keys for each collaborator individually. Collaborators are required to install all service dependencies on their local device if they wish to test code on their localhost. A collaborate should always **FORK** the repo from the main master and fetch changes from the upstream repo so reality is controlled by one admin responsible for approving all changes. New dependencies should be added to the Dockerfile, **NOT** to the repo files. Collaborators should test changes to Dockerfile locally before making a pull request to merge any new dependencies:_  

```
docker build -t test-image .
```

_.gitignore and .dockerignore have already been installed in key locations. To prevent unintended file proliferation through version control & provisioning, add/edit .gitignore and .dockerignore to include all new:_  

1. local environments folders
2. localhost dependencies
3. configuration files with credentials and local variables