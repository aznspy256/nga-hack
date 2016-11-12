__author__ = 'rcj1492'
__created__ = '2015.10'
__license__ = 'MIT'

'''
Flask Documentation
http://flask.pocoo.org/docs/0.11/deploying/wsgi-standalone/#gevent
'''

# create init path to sibling folders
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# construct flask app object
from flask import Flask, request, session, jsonify, url_for, render_template, redirect
app = Flask(import_name=__name__)

# initialize logging and debugging
import logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
app.config['ASSETS_DEBUG'] = False

# import request and response constructors
from labpack.parsing.flask import extract_request_details

# retrieve tunnel configurations
from labpack.records.settings import compile_settings
tunnel_config = compile_settings('models/system-model.json', '../cred/system.yaml')

# compile oauth authorization url map
from server.utils import compile_url_map
oauth_url_map = compile_url_map('models/oauth-model.json', '../cred')

# construct request handler
from server.utils import handle_request_wrapper
handle_request = handle_request_wrapper(app)

# construct tunnel request model
from jsonmodel.validators import jsonModel
from labpack.records.settings import load_settings
control_model = jsonModel(load_settings('models/control-request.json'))

# construct the dashboard view with oauth token variables
@app.route('/')
def landing_page():
    request_details = extract_request_details(request)
    template_kwargs = {}
    if oauth_url_map:
        service_list = list(oauth_url_map.keys())
        template_kwargs['auth_url'] = oauth_url_map[service_list[0]]
        template_kwargs['auth_name'] = service_list[0].capitalize()
        if 'oauth' in request_details['params'].keys():
            if request_details['params']['oauth'] in oauth_url_map.keys():
                service_name = request_details['params']['oauth']
                template_kwargs['auth_url'] = oauth_url_map[service_name]
                template_kwargs['auth_name'] = service_name.capitalize()
    return render_template('dashboard.html', **template_kwargs), 200

# construct OAuth endpoint
@app.route('/authorize/<service_name>')
def authorize_route(service_name=''):
    request_details = extract_request_details(request)
# construct default response
    template_name = 'dashboard.html'
    template_kwargs = {
        'service_name': service_name,
        'auth_code': '',
        'access_token': ''
    }
    if 'code' in request_details['params'].keys():
        template_kwargs['auth_code'] = request_details['params']['code']
# relay request details to server
    relay_host = tunnel_config['system_ip_address']
    relay_port = tunnel_config['server_system_port']
    relay_url = 'http://%s:%s/tunnel' % (relay_host, relay_port)
    response_details, status_code = handle_request(relay_url, request_details)
# alter default response based upon server details
    if 'redirect_url' in response_details.keys():
        return redirect(response_details['redirect_url'])
    elif 'template_kwargs' in response_details.keys():
        template_kwargs = response_details['template_kwargs']
        if 'template_name' in response_details.keys():
            template_name = response_details['template_name']
    return render_template(template_name, **template_kwargs), status_code

# construct tunnel control endpoint
@app.route('/control', methods=['POST'])
def control_route():
    request_details = extract_request_details(request)
    control_details = control_model.ingest(**request_details['json'])
# validate tunnel token
    tunnel_token = control_details['token']
    server_token = tunnel_config['tunnel_control_token']
    if not tunnel_token or not server_token or (tunnel_token != server_token):
        return jsonify({'error': 'access_denied'}), 400
# retrieve tunnel subdomain
    tunnel_subdomain = tunnel_config['tunnel_subdomain_name']
    if 'subdomain' in request_details['json'].keys():
        if request_details['json']['subdomain']:
            tunnel_subdomain = control_details['subdomain']
    if not tunnel_subdomain:
        error_msg = 'subdomain must be a lower case alphabetic string with no more than 63 characters.'
        return jsonify({'error': error_msg}), 404
# retrieve tunnel port
    tunnel_port = 5000
    if tunnel_config['tunnel_container_port']:
        tunnel_port = tunnel_config['tunnel_container_port']
    elif tunnel_config['tunnel_system_port']:
        tunnel_port = tunnel_config['tunnel_system_port']
# handle action type
    if control_details['action'] == 'open':
        from server.utils import open_localtunnel
        status_msg = open_localtunnel(tunnel_subdomain, tunnel_port)
        app.logger.debug(status_msg)
        return jsonify({'status': status_msg}), 200
    elif control_details['action'] == 'close':
        from server.utils import close_localtunnel
        status_msg = close_localtunnel(tunnel_subdomain, tunnel_port)
        app.logger.debug(status_msg)
        return jsonify({'status': status_msg}), 200
    else:
        error_msg = 'action must be either "open" or "close"'
        return jsonify({'error': error_msg}), 404

# construct the catchall for URLs which do not exist
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# initialize the test wsgi localhost server
if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', 5002), app)
    app.logger.debug('Tunnel started.')
    http_server.serve_forever()
