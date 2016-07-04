# coding: utf-8
import signal
import gevent
import subprocess
import time
import tempfile
import datetime


class WorkerManager(object):
    def __init__(self, config, notifier):
        self.config = config
        self.notifier = notifier
        self.workers = dict((d['name'], Worker(notifier=notifier, **d)) for d in config)

    def __getattr__(self, k, default=None):
        return getattr(self.workers, k, default)


class Worker(object):
    def __init__(self, name, cmd=None, cwd=None, env=None, stop_signal=signal.SIGTERM, timeout=300, notifier=None):
        self.name = name
        self.cmd = cmd
        self.args = cmd
        self.timeout = timeout
        self.cwd = cwd
        self.env = env
        self.stop_signal = stop_signal
        self.process = None
        self.output = None
        self.is_running = False
        self.return_code = None
        self.notifier = notifier

    def notify(self, content):
        if not self.notifier:
            return
        self.notifier.notify(content)

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
            self.process.send_signal(self.stop_signal)
            self.notify('🔫 %s\n@%s' % (self.name, datetime.datetime.now()))

    def _run(self, args=None):
        if self.is_running:
            return

        self.args = args or self.args
        if not self.args:
            raise ValueError

        self.output = tempfile.NamedTemporaryFile()
        self.is_running = True
        self.notify('🏃 %s\n@%s' % (self.name, datetime.datetime.now()))

        try:
            self.process = process = subprocess.Popen(self.args, stdout=self.output, stderr=self.output, env=self.env, cwd=self.cwd, shell='/bin/bash')
        except:
            self.is_running = False
            self.notify('❌ %s\n@%s' % (self.name, datetime.datetime.now()))
            raise

        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout:
                self.kill()

            if process.poll() is not None:
                self.is_running = False
                break
            time.sleep(1)

        self.return_code = process.returncode
        if self.return_code == 0:
            self.notify('🎉 %s\n@%s' % (self.name, datetime.datetime.now()))
        else:
            self.notify('❌ %s\n@%s' % (self.name, datetime.datetime.now()))
