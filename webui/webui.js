var imagesPath = "/home/benjamin/projects/cv/CV-Maze-Solver/webui/uploads";
var mazeSolverPath = "/home/benjamin/projects/cv/CV-Maze-Solver";
var Images = new FS.Collection("images", {
  stores: [new FS.Store.FileSystem("image", {path: imagesPath})]
})

var imageId = undefined;

if(Meteor.isClient) {
  Dropzone.autoDiscover = false;
  Template.upload.rendered = function() {
    $('#dropzone').dropzone({
      maxFiles: 1,
      url: "/file-upload",
      accept: function(file, done) {
        Images.insert(file, function(err, fileObj) {
          if(err) {
            alert(err);
          }
          else {
            imageId = fileObj._id;
          }
        })
      }
    })
  };

  Template.options.events({
    'click #solve': function(event) {
      console.log(imageId);
      Streamy.emit('solve', {imageId: imageId, handdrawn: $('#handdrawn').val()});
    }
  });
}

if(Meteor.isServer) {
  exec = Npm.require('child_process').exec;

  Meteor.startup(function () {
  });

  Streamy.on('solve', function(d, s) {
    fileObj = Images.findOne({_id: d.imageId});
    exec("python2 " + mazeSolverPath + "/mazesolver.py " + imagesPath + "/" + fileObj.copies.image.key,
      function(error, stdout, stderr) {
        if(error !== null) {
          console.log('stderr: ' + stderr);
          console.log('error: ' + error);
        }
        else {
          stdout = stdout.split('---GRAPH START---')[1]
          stdout = stdout.split('---').slice(1)
          for (var i = 0; i < stdout.length; i++) {
            console.log(stdout[i]);
          };
        }
      });
  });
}
