# __author__ = "Amos"
# Email: 379833553@qq.com

from apps import __version__
import os
import sys
import subprocess
import time
import argparse
import platform


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

try:
    from config import config as CONFIG
except ImportError:
    print('Could not find config file, Please check the integrity of the project.')
    sys.exit(1)

OS_TYPE = platform.system()
APPS_DIR = os.path.join(BASE_DIR, 'apps')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
HTTP_HOST = CONFIG.HTTP_BIND_HOST or '127.0.0.1'
HTTP_PORT = CONFIG.HTTP_LISTEN_PORT or 8080

WORKERS = CONFIG.WORKERS or 4
DEBUG = CONFIG.DEBUG
all_services = ['gunicorn']
START_TIMEOUT = CONFIG.START_TIMEOUT or 10


def make_migrations():
    print('Check database structure change ...')
    os.chdir(APPS_DIR)
    subprocess.call('python3 manage.py makemigrations', shell=True)
    subprocess.call('python3 manage.py migrate', shell=True)


def prepare():
    make_migrations()


def get_pid_file_path(service):
    return os.path.join(TMP_DIR, '{}.pid'.format(service))


def get_log_file_path(service):
    return os.path.join(LOG_DIR, '{}.log'.format(service))


def parse_service(service):
    if service == 'all':
        return all_services
    else:
        return [service]


def get_pid(service):
    pid_file = get_pid_file_path(service)
    if os.path.isfile(pid_file):
        with open(pid_file) as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
    return 0


def is_running(service):
    pid = get_pid(service)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def start_gunicorn():
    print("\n- Start Gunicorn WSGI HTTP Server")
    prepare()
    service = 'gunicorn'
    bind = '{}:{}'.format(HTTP_HOST, HTTP_PORT)
    log_format = '%(h)s %(t)s "%(r)s" %(s)s %(b)s '
    pid_file = get_pid_file_path(service)
    log_file = get_log_file_path(service)

    cmd = [
        'gunicorn', 'jumpserver.wsgi',
        '-b', bind,
        '-w', str(WORKERS),
        '--access-logformat', log_format,
        '-p', pid_file,
        '-access-logfile', log_file,
        '--daemon',
    ]
    if DEBUG:
        cmd.append('--reload')
    p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, cwd=APPS_DIR)
    return p


def start_service(service):
    print(time.ctime())
    print('Lpyy version {}, by Amos'.format(__version__))

    services_handler = {
        'gunicorn': start_gunicorn,
    }

    services_set = parse_service(service)
    process = []
    for i in services_set:
        if is_running(i):
            show_service_status(i)
            continue
        func = services_handler.get(i)
        p = func()
        process.append(p)

    now = time.time()
    for i in services_set:
        while not is_running(i):
            if int(time.time()) - now < START_TIMEOUT:
                time.sleep(1)
                continue
            else:
                print("Error: {} start error".format(i))
                stop_service(service, sig=9)
                return

    print()
    show_service_status(service)


def stop_service(service,sig=15):
    services_set = parse_service(service)
    for i in services_set:
        if not is_running(i):
            show_service_status(i)
            continue
        print("Stop service: {}".format(i))
        pid = get_pid(i)
        os.kill(pid, sig)


def show_service_status(service):
    services_set = parse_service(service)
    for i in services_set:
        if is_running(i):
            pid = get_pid(i)
            print("{} is running: {}".format(i,pid))
        else:
            print("{} is stopped".format(i))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
    Lpyy service control tools
    
    Example:
    
    %(prog)s start;
    """)

    parser.add_argument(
        'action', type=str,
        choices=('start','stop','status','restart'),
        help='Action to run')

    parser.add_argument(
        "service", type = str, default = "all", nargs = "?",
        choices = all_services.append("all"),
        help = "The service to start"
    )
    args = parser.parse_args()

    if args.action == 'start':
        start_service(args.service)
    elif args.action == 'stop':
        stop_service(args.service)
    elif args.action == 'status':
        show_service_status(args.service)
    elif args.action == 'restart':
        stop_service(args.service)
        time.sleep(5)
        start_service(args.service)
    else:
        show_service_status(args.service)