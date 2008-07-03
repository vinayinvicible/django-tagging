
import os

from paste.deploy import loadwsgi

from spawning import spawning_controller


def config_factory(args):
    if 'config_url' in args:
        config_url = args['config_url']
        relative_to = args['relative_to']
        global_conf = args['global_conf']
    else:
        config_file = os.path.abspath(args['args'][0])
        config_url = 'config:%s' % (os.path.basename(config_file), )
        relative_to = os.path.dirname(config_file)
        global_conf = {}

    ctx = loadwsgi.loadcontext(
        loadwsgi.SERVER,
        config_url,
        relative_to=relative_to,
        global_conf=global_conf)

    return {
        'dev': ctx.global_conf.get('debug') == 'true',
        'host': ctx.local_conf['host'],
        'port': int(ctx.local_conf['port']),
        'num_processes': int(ctx.local_conf.get('num_processes', 1)),
        'threadpool_workers': int(ctx.local_conf.get('threadpool_workers', 0)),
        'watch': [ctx.global_conf['__file__']],

        'app_factory': 'spawning.paste_factory.app_factory',
        'config_url': config_url,
        'relative_to': relative_to,
        'global_conf': ctx.global_conf
    }


def app_factory(config):
    return loadwsgi.loadapp(
        config['config_url'],
        relative_to=config['relative_to'],
        global_conf=config['global_conf'])


def server_factory(global_conf, host, port, *args, **kw):
    config_url = 'config:' + os.path.split(
        global_conf['__file__'])[1]
    relative_to = global_conf['here']

    def run(app):
        spawning_controller.run_controller(
            'spawning.paste_factory.config_factory',
            {'config_url': config_url, 'relative_to': relative_to, 'global_conf': global_conf})

    return run
