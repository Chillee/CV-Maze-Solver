var imagesPath = "/tmp/uploads";
var mazeSolverPath = "/home/benjamin/projects/cv/CV-Maze-Solver/src";
var Images = new FS.Collection("images", {
  stores: [new FS.Store.FileSystem("image", {path: imagesPath})]
})

var imageId = undefined;
var imageFile = undefined;

if(Meteor.isClient) {
  var handle = undefined;
  Dropzone.autoDiscover = false;

  function uploadFile(file) {
    Images.insert(file, function(err, fileObj) {
      if(err) {
        alert(err);
        $('#process').removeClass('disabled');
      }
      else {
        imageId = fileObj._id;
        var cursor = Images.find({_id: fileObj._id});
        var liveQuery = cursor.observe({
          changed: function(newImage, oldImage) {
            if(newImage.isUploaded()) {
              liveQuery.stop();
              $('#process').removeClass('disabled');
            }
          }
        })
      }
    });
  }

  Template.upload.rendered = function() {
    $('.ui.dropdown').dropdown();
    $('#dropzone').dropzone({
      maxFiles: 1,
      url: "/file-upload",
      accept: function(file, done) {
        $('#solver-ui').hide();
        $('#process').addClass('disabled');
        imageFile = file;
        uploadFile(file);
      }
    });
  };

  Template.upload.events({
    'change #preset-maze': function(event) {
      imageFile = null;
      var xhr = new XMLHttpRequest();
      xhr.open("GET", $('#preset-maze-top').dropdown('get value'));
      xhr.responseType = "blob";
      xhr.onload = function() {
        console.log(xhr.response);
        imageFile = xhr.response;
        uploadFile(xhr.response);
      };
      xhr.send();
    }
  });

  Session.set('processingMaze', false);
  Session.set('graphData', undefined);
  Session.set('useScale', false);

  Template.options.helpers({
    'processingMaze': function() { return Session.get('processingMaze'); },
    'processingDone': function() { return Session.get('processingDone'); },
    'useScale': function() { return Session.get('useScale'); }
  });

  Template.options.events({
    'click #process': function(event) {
      var scale = 0.0;
      if(Session.get('useScale')) {
        scale = parseFloat($('#scale').val());
      }
      Streamy.emit('solve', {imageId: imageId, handdrawn: $('#handdrawn').val(), scale: scale});
      Session.set('processingMaze', true);
    },
    'click #use-scale': function(event) {
      Session.set('useScale', !Session.get('useScale'));
    }
  });

  Session.set('showGraph', false);
  Template.solverUi.events({
    'click #show-graph': function(event) {
      Session.set('showGraph', !Session.get('showGraph'));
    }
  })

  Tracker.autorun(function() {
    if(Session.get('processingMaze')) {
      $('#process').addClass('disabled');
    }
    else {
      $('#process').removeClass('disabled');
    }
  });

  Streamy.on('graph', function(d, s) {
    Session.set('graphData', d);
    Session.set('processingMaze', false);
    $('#solver-ui').show();

    var ctx = $('canvas')[0].getContext('2d');
    var img = new Image();
    img.onload = function() {
      var aspect = img.width / img.height;
      var width = window.innerWidth - 50;
      var height = width / aspect;
      var sizeRatio = width / img.width;
      /*$('canvas')[0].width = width;
      $('canvas')[0].height = height;*/
      ctx.canvas.width = width;
      ctx.canvas.height = height;
      ctx.drawImage(img, 0, 0, width, height);

      if(handle !== undefined) {
        handle.stop();
      }
      handle = Tracker.autorun(function() {
        if(Session.get('showGraph')) {
          for(var i = 0; i < d.graph.length; i++) {
            var node = d.graph[i];
            ctx.beginPath();
            ctx.arc(node.pos[0] * sizeRatio, node.pos[1] * sizeRatio, 3, 0, 2 * Math.PI, false);
            ctx.fillStyle = 'green';
            ctx.fill();
            ctx.lineWidth = 1;
            ctx.strokeStyle = 'black';
            ctx.stroke();

            for(var i2 = 0; i2 < node.connections.length; i2++) {
              var other = d.graph[node.connections[i2].other];
              ctx.beginPath();
              ctx.moveTo(node.pos[0] * sizeRatio, node.pos[1] * sizeRatio);
              ctx.lineTo(other.pos[0] * sizeRatio, other.pos[1] * sizeRatio);
              ctx.lineWidth = 1;
              ctx.strokeStyle = 'green';
              ctx.stroke();
            }
          }
        }
        else {
          ctx.drawImage(img, 0, 0, width, height);
        }
      });

      var points = [];

      function dijkstra(start, end) {
        var distances = [];
        var prev = [];
        for(var i = 0; i < d.graph.length; i++) {
          distances.push(Number.POSITIVE_INFINITY);
          prev.push(-1);
        }
        distances[start] = 0;

        var curNodes = new PriorityQueue({comparator: function(a, b) {
          return distances[a] < distances[b];
        }});
        curNodes.queue(start);

        while(curNodes.length != 0) {
          var index = curNodes.dequeue();
          var node = d.graph[index];

          for(var i = 0; i < node.connections.length; i++) {
            var conn = node.connections[i];
            newDist = distances[index] + conn.dist;
            if(newDist < distances[conn.other]) {
              distances[conn.other] = newDist;
              prev[conn.other] = index;
              curNodes.queue(conn.other);
            }
          }
        }

        var curNode = end;
        var path = [];
        while(curNode != -1) {
          path.push(curNode);
          curNode = prev[curNode];
        }
        return path;
      }

      function findClosest(x, y) {
        var closestDist = Number.POSITIVE_INFINITY;
        var closestId = -1;
        for(var i = 0; i < d.graph.length; i++) {
          var dx = d.graph[i].pos[0] - x;
          var dy = d.graph[i].pos[1] - y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if(dist < closestDist) {
            closestDist = dist;
            closestId = i;
          }
        }
        var node = d.graph[closestId];
        return closestId;
      }

      function getMousePos(canvas, evt) {
        var rect = canvas.getBoundingClientRect();
        return {
          x: evt.clientX - rect.left,
          y: evt.clientY - rect.top
        };
      }

      $('canvas')[0].addEventListener('click', function(event) {
        var pos = getMousePos(ctx.canvas, event);
        var x = pos.x / sizeRatio;
        var y = pos.y / sizeRatio;
        if(points.length == 0) {
          points.push(findClosest(x, y));
        }
        else {
          points.push(findClosest(x, y));
          var path = dijkstra(points[0], points[1]);
          ctx.drawImage(img, 0, 0, width, height);
          handle.invalidate();
          Tracker.flush();
          for(var i = 0; i < path.length-1; i++) {
            var a = d.graph[path[i]];
            var b = d.graph[path[i+1]];
            ctx.beginPath();
            ctx.moveTo(a.pos[0] * sizeRatio, a.pos[1] * sizeRatio);
            ctx.lineTo(b.pos[0] * sizeRatio, b.pos[1] * sizeRatio);
            ctx.strokeStyle = 'blue';
            ctx.lineWidth = 2;
            ctx.stroke();
          }
          points = [];
        }
      }, false);
    }
    img.src = URL.createObjectURL(imageFile);
  })
}

if(Meteor.isServer) {
  var TOK_CLIENT_START_PROCESSING = 0;
  var TOK_SERVER_DONE_PROCESSING = 0;

  var net = Npm.require('net');

  //var servers = [['localhost', 8007]];
  //var servers = [['137.22.4.49', 8007]];
  var servers = [
    ['cmc306-12.mathcs.carleton.edu', 8007],
    ['cmc306-10.mathcs.carleton.edu', 8007],
    ['cmc306-09.mathcs.carleton.edu', 8007]
  ]
  var serverLoads = [];
  for(var i = 0; i < servers.length; i++) {
    serverLoads.push(0);
  }

  Meteor.startup(function () {
  });

  Streamy.on('solve', function(d, s) {
    fileObj = Images.findOne({_id: d.imageId});

    function tryConnect() {
      var serverIdx = serverLoads.indexOf(Math.min.apply(Math, serverLoads));
      var server = servers[serverIdx];
      console.log("Sending job to server " + server[0] + ":" + server[1])
      serverLoads[serverIdx] += 1;

      var conn = net.createConnection({
        port: server[1],
        host: server[0]
      }, function() {
        var stream = fileObj.createReadStream('images');

        var ext = fileObj.extension();
        if(ext[0] === undefined) {
          ext = 'png';
        }
        var buf = new Buffer([TOK_CLIENT_START_PROCESSING, d.handdrawn ? 1 : 0,
          ext[0].charCodeAt(0),
          ext[1].charCodeAt(0),
          ext[2].charCodeAt(0),
          0,0,0,0]);
        buf.writeFloatBE(d.scale, 5);
        var buffers = [];
        stream.on('data', function(buffer) {
          buffers.push(buffer);
        });
        stream.on('end', function() {
          var buffer = Buffer.concat(buffers);
          var lengthBuf = new Buffer(4);
          lengthBuf.writeUInt32BE(buffer.length, 0);
          buf = Buffer.concat([buf, lengthBuf, buffer]);
          conn.write(buf);

          var allData = "";
          conn.on('data', function(data) {
            allData = allData + data;
          });
          conn.on('end', function() {
            console.log("Job complete, sending back to client");
            serverLoads[serverIdx] -= 1;
            var graph = JSON.parse(allData);
            Streamy.emit('graph', {graph: graph}, s);
          });
        });
      });
      conn.on('error', function(ex) {
        console.log("Failed to connect to server " + server[0]);
        console.log("Attempting to connect to a different server.");
        tryConnect();
      });
    };
    tryConnect();
  });
}
