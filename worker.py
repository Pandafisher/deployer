#! coding: utf-8
import gevent
import subprocess
import time
import tempfile


class WorkerManager(object):
    def __init__(self, config):
        self.config = config
        self.workers = dict((d['name'], Worker(**d)) for d in config)

    def __getattr__(self, k, default=None):
        return getattr(self.workers, k, default)


class Worker(object):
    def __init__(self, name, args=None, cwd=None, env=None, timeout=300):
        self.name = name
        self.args = args
        self.timeout = timeout
        self.cwd = cwd
        self.env = env
        self.process = None
        self.output = None
        self.is_running = False

    def poll_output(self):
        if not self.output:
            return ''
        with open(self.output.name) as f:
            return f.read()

    def run(self, args=None):
        if self.is_running:
            return False

        gevent.spawn(self._run, args)
        return True

    def kill(self):
        if self.is_running:
            self.process.terminate()

    def _run(self, args=None):
        if self.is_running:
            return

        self.args = args or self.args
        if not self.args:
            raise ValueError

        self.output = tempfile.NamedTemporaryFile()
        self.is_running = True
        try:
            self.process = process = subprocess.Popen(self.args, stdout=self.output, stderr=self.output, env=self.env, cwd=self.cwd, shell=True)
        except:
            self.is_running = False
            return

        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout:
                process.terminate()

            if process.poll() is not None:
                self.is_running = False
                break
            time.sleep(1)

        return process.returncode
