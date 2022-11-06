(function (epoch) {
  var errorCount = 0;
  var req = new XMLHttpRequest();

  req.onloadend = function () {
    if (parseFloat(this.responseText) > epoch) {
      location.reload()
      return;
    }
    var launchNext = livereload.bind(this, epoch);
    if (this.status === 200) {
      errorCount = 0
      launchNext();
    } else {
      if (errorCount++ > 2) { return }
      setTimeout(launchNext, 2000);
    }
  };
  req.open("GET", "/livereload/" + epoch);
  req.send();

  console.log('Enabled live reload');

})(__EPOCH__);
