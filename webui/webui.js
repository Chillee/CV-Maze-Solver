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

  Template.upload.rendered = function() {
    $('#dropzone').dropzone({
      maxFiles: 1,
      url: "/file-upload",
      accept: function(file, done) {
        $('#solver-ui').hide();
        $('#process').addClass('disabled');
        imageFile = file;

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
        })
      }
    })
  };

  Session.set('processingMaze', false);
  Session.set('graphData', undefined);
  Template.options.helpers({
    'processingMaze': function() { return Session.get('processingMaze'); },
    'processingDone': function() { return Session.get('processingDone'); }
  });

  Template.options.events({
    'click #process': function(event) {
      Streamy.emit('solve', {imageId: imageId, handdrawn: $('#handdrawn').val()});
      Session.set('processingMaze', true);
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
  exec = Npm.require('child_process').exec;

  Meteor.startup(function () {
  });

  Streamy.on('solve', function(d, s) {
    fileObj = Images.findOne({_id: d.imageId});
    var cmd = "python2 " + mazeSolverPath + "/getgraph.py " + imagesPath + "/" + fileObj.copies.image.key;
    if(d.handdrawn) {
      cmd = cmd + " -d";
    }

    console.log("Solving Maze");
    exec(cmd,
      { maxBuffer: 1024*5000 },
      function(error, stdout, stderr) {
        console.log("Done");
        if(error !== null) {
          console.log('stderr: ' + stderr);
          console.log('error: ' + error);
        }
        else {
          stdout = stdout.split('---GRAPH START---')[1]
          stdout = stdout.split('---').slice(1)
          var graph = []
          for(var i = 0; i < stdout.length; i++) {
            var lines = stdout[i].split('\n');
            var pos = lines[1].split(',');
            var x = parseFloat(pos[0]);
            var y = parseFloat(pos[1]);
            lines = lines.slice(2);

            var node = {
              pos: [x,y],
              id: i,
              connections: []
            };

            for(var i2 = 0; i2 < lines.length - 1; i2++) {
              var line = lines[i2].split(',');
              var other = parseInt(line[0], 10);
              var dist = parseFloat(line[1]);
              node.connections.push({
                other: other,
                dist: dist
              })
            }

            graph.push(node);
          }
          Streamy.emit('graph', { graph: graph }, s);
        }
      });
  });
}
