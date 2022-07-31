
function togglestreams() {
  const targetDiv = document.getElementById("scroll_live");
  if (targetDiv.style.visibility == "visible") {
    targetDiv.style.visibility = "hidden";
    targetDiv.style.display = "none";
  } else {
    targetDiv.style.visibility = "visible";
    targetDiv.style.display = "block";
    
  }
};

function togglestreamshistory() {
  const targetDiv = document.getElementById("scroll_history");
  if (targetDiv.style.visibility == "visible") {
    targetDiv.style.visibility = "hidden";
    targetDiv.style.display = "none";
  } else {
    targetDiv.style.visibility = "visible";
    targetDiv.style.display = "block";
    
  }
};

function togglestreamsoverall() {
  const targetDiv = document.getElementById("scroll_overall");
  if (targetDiv.style.visibility == "visible") {
    targetDiv.style.visibility = "hidden";
    targetDiv.style.display = "none";
  } else {
    targetDiv.style.visibility = "visible";
    targetDiv.style.display = "block";
    
  }
};

function redirect(path) {
    console.log(path);
    window.open('/' + path)
    //location.href = '/' + path;
};
