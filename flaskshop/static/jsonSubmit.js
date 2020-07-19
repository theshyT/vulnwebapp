// Sending and receiving data in JSON format using POST method
//
//function forceJSON() {
//  var xhr = new XMLHttpRequest();
//  var url = "url";
//  xhr.open("POST", url, true);
//  xhr.setRequestHeader("Content-Type", "application/json");
//  xhr.onreadystatechange = function () {
//      if (xhr.readyState === 4 && xhr.status === 200) {
//          var json = JSON.parse(xhr.responseText);
//          console.log(json.email + ", " + json.password);
//      }
//  };
//  var data = JSON.stringify({"name": "hey@mail.com", "message": "101010"});
//  xhr.send(data);
//  window.location.href = "localhost:5000/"
//}

function forceJSON(email, title) {
    var xhr = new XMLHttpRequest();
    var url = "/json";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
          var json = JSON.parse(xhr.responseText);
          console.log(xhr.responseText);
      }
    };
    var data = JSON.stringify({"name": email, "message": title});
    xhr.send(data);
}
