Vue.config.delimiters = ['${', '}']
var app = new Vue({
  el: '#app',
  data: {
    workers: [],
    current: {}
  },
  ready: function () {
    this.fetch()
    setInterval(this.fetch.bind(this), 5000)
  },
  methods: {
    fetch: function () {
      var that = this
      $.ajax({
        method: "GET",
        url: '/workers'
      })
      .done(function( result ) {
        var tmpWorkers = result.content.workers
        if (that.workers.length === 0) {
          that.workers = tmpWorkers;
          that.current = that.workers[0]
        } else {
          for (var i=0; i<tmpWorkers.length; i++) {
            var worker = that.getWorkerByName(tmpWorkers[i].name)
            if (worker) {
              var oldRunning = worker.is_running
              Vue.util.extend(worker, tmpWorkers[i])
              if (!worker.is_running) {
                clearInterval(worker.interval)
              } else {
                if (oldRunning !== worker.is_running || !worker.log) {
                  clearInterval(worker.interval);
                  (function (runningWorker) {
                    worker.interval = setInterval(function () {
                      that.output(runningWorker)
                    }, 2000)
                  })(worker);
                }
              }
            }
          }
        }
      })
      .fail(function () {
        if (that.workers.length) alert('获取数据失败！')
      })
    },
    selectWork: function (worker) {
      var that = this
      this.current = worker
    },
    deploy: function () {
      var target = this.getWorkerByName(this.current.name)
      var project = prompt('请输入您要部署的项目名称 ' + target.name);
      if (project.name !== target.name) {
        alert('输入有误！')
        return;
      }
      var that = this;
      Vue.set(target, 'deployPending', true)
      $.ajax({
        method: "POST",
        url: target.deploy_url
      })
      .done(function( data ) {
        target.is_running = true
        target.interval = setInterval(that.output.bind(that), 2000)
      })
      .fail(function () {
        alert('deploy error')
      })
      .always(function() {
        Vue.set(target, 'deployPending', false)
      })
    },
    kill: function () {
      if (!confirm('您确定要停止吗？')) {
        return;
      }
      var target = this.getWorkerByName(this.current.name)
      Vue.set(target, 'killPending', true)
       $.ajax({
        method: "POST",
        url: target.kill_url
      })
      .done(function( data ) {
        alert('终止请求已发送！')
        // target.is_running = false
        clearInterval(target.interval)
      })
      .fail(function () {
        alert('kill error')
      })
      .always(function() {
        Vue.set(target, 'killPending', false)
      })
    },
    output: function (worker) {
      var target = worker || this.getWorkerByName(this.current.name)
      $.ajax({
        method: "GET",
        url: target.poll_output_url
      })
      .done(function( data ) {
        Vue.set(target, 'log', data.content.output)
        Vue.nextTick(function() {
          var logEle = document.getElementById('log-output')
          logEle.scrollTop = logEle.scrollHeight
        })
      })
    },
    getWorkerByName: function (name) {
      for(var i=0; i<this.workers.length; i++) {
        var worker = this.workers[i];
        if (worker.name === name) {
          return worker
        }
      }
    }
  }
})