__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

def retrieve_config_details(model_path, config_path):

# parse config name from model path
    import re
    config_pattern = re.compile('models/(.*)?\\-model\\.json')
    config_name = config_pattern.search(model_path).group(1)

# construct configuration model and default details
    from labpack.records.settings import ingest_environ, load_settings
    from jsonmodel.validators import jsonModel
    config_model = jsonModel(load_settings(model_path))
    default_details = config_model.ingest(**{})

# retrieve environmental variables and file details
    environ_details = ingest_environ()
    file_details = {}
    try:
        from os import path
        config_file = '%s.yaml' % config_name
        file_path = path.join(config_path, config_file)
        file_details = load_settings(file_path)
    except:
        pass

# construct config details from (first) envvar, (second) file, (third) default
    config_details = {}
    for key in default_details.keys():
        if key.upper() in environ_details.keys():
            config_details[key] = config_model.validate(environ_details[key.upper()], '.%s' % key)
        elif key in file_details.keys():
            config_details[key] = config_model.validate(file_details[key], '.%s' % key)
        else:
            config_details[key] = default_details[key]

    return config_details

def compile_authorize_url(oauth_details):
    from labpack.activity.moves import movesOAuth
    init_kwargs = {
        'client_id': oauth_details['oauth_client_id'],
        'client_secret': oauth_details['oauth_client_secret']
    }
    moves_oauth = movesOAuth(**init_kwargs)
    url_kwargs = {
        'device_type': 'web',
        'redirect_uri': oauth_details['oauth_redirect_uri'],
        'state_value': 'unittest',
        'service_scope': oauth_details['oauth_service_scope'].split()
    }
    authorize_url = moves_oauth.generate_url(**url_kwargs)
    return authorize_url

def compile_url_map(model_path, cred_folder):

    from labpack.records.settings import ingest_environ, load_settings
    from jsonmodel.validators import jsonModel
    config_model = jsonModel(load_settings(model_path))

    url_map = {}

    from os import listdir, path

    cred_list = []
    try:
        cred_list = listdir(cred_folder)
    except:
        pass

    for file_name in cred_list:
        try:
            file_title = file_name.replace('.yaml', '')
            oauth_details = {}
            oauth_match = True
            cred_config = load_settings(path.join(cred_folder, file_name))
            for key in config_model.schema.keys():
                new_key = key.replace('oauth', file_title)
                if new_key not in cred_config.keys():
                    oauth_match = False
                    break
                else:
                    value = cred_config[new_key]
                    oauth_details[key] = config_model.validate(value, '.%s' % key)
            if oauth_match:
                url_map[file_title] = compile_authorize_url(oauth_details)
        except:
            pass

    return url_map

def handle_request_wrapper(app_object):
    def handle_request(url, request_details):
        import requests
        try:
            response = requests.post(url, json=request_details)
            return response.json(), response.status_code
        except requests.exceptions.ConnectionError:
            error_msg = '%s is not available.' % url
            pass
        except requests.exceptions.InvalidURL:
            error_msg = '%s is not a valid url.' % url
            missing = False
            multiple = False
            helper_msg = ' '
            if url.find('://:'):
                missing = True
                multiple = True
                helper_msg += 'system_ip_address '
            if url.find(':/tunnel'):
                missing = True
                if multiple:
                    helper_msg += 'and '
                helper_msg += 'system_server_port '
            if missing:
                if multiple:
                    helper_msg += 'are '
                else:
                    helper_msg += 'is '
                helper_msg += 'missing.'
                error_msg += helper_msg
            pass
        app_object.logger.debug(error_msg)
        error_details = {
            'template_name': '404.html',
            'template_kwargs': { 'error_message': error_msg }
        }
        if 'code' in request_details['params'].keys():
            help_msg = 'Code: %s' % request_details['params']['code']
            error_details['template_kwargs']['help_message'] = help_msg
        return error_details, 404
    return handle_request

def open_localtunnel(subdomain_name, port_number, tunnel_provider='localtunnel.me'):

    import shutil

# construct command args
    if tunnel_provider == 'localtunnel.me':
        shell_command = shutil.which('lt')
        command_args = ['--port', str(port_number), '--subdomain', subdomain_name, '&']
        command_args.insert(0, shell_command)
    else:
        raise Exception('%s is not currently supported.' % tunnel_provider)

# open process
    import subprocess
    subprocess.Popen(command_args)

    status_message = 'tunnel %s open' % subdomain_name

    return status_message

def close_localtunnel(subdomain_name, port_number, tunnel_provider='localtunnel.me'):

    import psutil
    from psutil import AccessDenied

    if tunnel_provider == 'localtunnel.me':
        port_flag = '--port'
        subdomain_flag = '--subdomain'
        options_set = { subdomain_name, subdomain_flag, port_flag, str(port_number) }
    else:
        raise Exception('%s is not currently supported.' % tunnel_provider)

# search processes for process name
    process_existed = False
    for process in psutil.process_iter():
        try:
            command_array = process.cmdline()
            if not options_set - set(command_array):
                process.terminate()
                status_msg = 'tunnel %s closed' % subdomain_name
                process_existed = True
                break
        except AccessDenied:
            pass

    if not process_existed:
        status_msg = 'tunnel %s does not exist' % subdomain_name

    return status_msg

if __name__ == '__main__':
    tunnel_config = retrieve_config_details('models/tunnel-model.json', '../cred')
    assert not tunnel_config['tunnel_container_port']
    import os
    os.environ['tunnel_container_port'] = '5000'
    tunnel_config = retrieve_config_details('models/tunnel-model.json', '../cred')
    assert tunnel_config['tunnel_container_port'] == 5000
    oauth_url_map = compile_url_map('models/oauth-model.json')
    assert oauth_url_map['moves'].find('code') > 0
    from flask import Flask
    app = Flask(import_name=__name__)
    handle_request = handle_request_wrapper(app)
    test_url = 'http://:/tunnel'
    response, status = handle_request(test_url, {'params': {}})
    assert response['template_kwargs']['error_message'].find('valid url') > 0
    test_url = 'http://%s:%s/tunnel' % (tunnel_config['system_ip_address'], tunnel_config['server_system_port'])
    response, status = handle_request(test_url, {'params':{'code':'happy'}})
    assert response['template_kwargs']['help_message'].find('happy') > 0
    # from labpack.randomization.randomlab import random_characters
    # from string import ascii_lowercase
    # subdomain_name = random_characters(ascii_lowercase, 32)
    # open_localtunnel(subdomain_name, 5000)
    # from time import sleep
    # sleep(5)
    # close_localtunnel(subdomain_name, 5000)



