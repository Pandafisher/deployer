#! coding: utf-8
from gevent import monkey
monkey.patch_all()


from flask import Flask, render_template, url_for
from worker import WorkerManager
from render import ok, error
from config import workers


worker_manager = WorkerManager(workers)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.mako', manager=worker_manager)


@app.route('/workers')
def workers():
    return ok({
        'workers': [{
            'name': name,
            'poll_output_url': url_for('.worker_poll_output', name=name, _external=True),
            'deploy_url': url_for('.worker_deploy', name=name, _external=True),
            'kill_url': url_for('.worker_kill', name=name, _external=True),
            'is_running': worker.is_running,
        } for name, worker in worker_manager.items()],
    })


@app.route('/workers/<name>/poll_output')
def worker_poll_output(name):
    worker = worker_manager.get(name)
    if not worker:
        return error(status_code=404)
    output = worker.poll_output()
    return ok({
        'output': output,
    })


@app.route('/workers/<name>/deploy', methods=['POST'])
def worker_deploy(name):
    worker = worker_manager.get(name)
    if not worker:
        return error(status_code=404)
    worker.run()
    return ok()


@app.route('/workers/<name>/kill', methods=['POST'])
def worker_kill(name):
    worker = worker_manager.get(name)
    if not worker:
        return error(status_code=404)
    worker.kill()
    return ok()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
