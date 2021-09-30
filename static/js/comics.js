
var select = new SlimSelect({
  select: '#multiple'
})

var offset;
var total;
var searchStart;

const btn = document.querySelector('button');

btn.onclick = function() {
  document.getElementById("grid").innerHTML='';  //remove previous search results
  offset = 0;
  total = 0;
  searchStart = false; //boolean used so intersectionObserver doesn't trigger on initial search
  loadComics()
}


function loadComics() {
  //stop request if the total comics available has been reached
      if (total != 0 && offset == total) {
        return;
      }

  document.getElementById("loader").style.display = "block"; //display loader while performing request
  const request = new XMLHttpRequest();
  request.onreadystatechange = function () {
    if (request.readyState == 4 && request.status == 200) {
      try {
        document.getElementById("loader").style.display = "none";

        let data = JSON.parse(request.responseText);
        let cards = document.getElementById("grid");
        if (data.data["total"] == 0) {
          cards.textContent = "Sorry, no comics were found featuring that combination of characters."
        }

        offset = offset + data["data"]["count"]; //update offset with no. of comics received
        total = data["data"]["total"];

        let template = document.getElementById("blank-card");

        //create a clone of the HTML comic card template and fill with data received
        for (let i = 0; i < data.data["count"]; i++) {
          let clone = template.content.cloneNode(true);
          // if (data.data.results[i]["thumbnail"]["path"].split === "")
          clone.querySelector("img").src = data.data.results[i]["thumbnail"]["path"] + "/portrait_uncanny.jpg";
          console.log(data.data.results[i]["thumbnail"]["path"])
          clone.querySelector("h1").textContent = data.data.results[i]["title"];


          for (let j = 0; j < data.data.results[i]["creators"]["available"]; j++) {
            clone.querySelector("p").textContent += capitalise(data.data.results[i]["creators"]["items"][j]["role"]) + ": " + data.data.results[i]["creators"]["items"][j]["name"] + "\r\n";
          }
          clone.querySelector("a").href = data.data.results[i]["urls"][0]["url"];
          cards.appendChild(clone);
        }

        //if user scrolls to end of page boolean will allow for intersectionobserver to make new request with updated offset
        searchStart = true;

      } catch (err) {
        console.log(err.message + " in " + request.responseText);
        return;
      }
    }
  };
  request.open('POST', '/load', true);
  var charactersAndOffset = select.selected();
  charactersAndOffset.push(offset);
  request.send(JSON.stringify(charactersAndOffset));
}



//intersection observer will continue to load comics for those characters with over 100 (request-limit)
const io = new IntersectionObserver(entries => {

  entries.forEach(entry => {
    if (select.selected().length == 0 || !searchStart) {
      return;
    }
    loadComics();
  });
});

//apply intersectionobserver to the div below the grid of comics cards
io.observe(document.getElementById("end-of-page"));

//function to capitalise comic creative team's roles
function capitalise(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}
