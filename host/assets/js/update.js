const loading = "<img src='/assets/img/loading.gif'/>";
const {title} = document;

function makeAllRequests() {
    "use strict";

    [...document.getElementsByTagName("tr")].forEach((tr, id, arr) => makeRequest(id));
}

function makeRequest(id) {
    "use strict";

    let items = document.getElementById("feed-" + id);

    items.innerHTML  = loading;
    fetch("update/" + id)
        .then((response) => {
            if (response.ok) {
                return response.json();
            }
            throw new Error("Something went wrong");
        })
        .then((data) => alertContents(data, id))
        .catch((error) => { console.log(error); });
}

function alertContents(data, id) {
    "use strict";

    let ret = data.count;
    let items = document.getElementById("feed-" + id);
    let sum = document.getElementById("sum");

    if (ret > 0) {
        sum.innerHTML = parseInt(sum.innerHTML, 10) + ret;
        document.title = "(" + sum.innerHTML + ") " + title;
        items.style.color = "green";
        ret = "⭐ (+ " + ret + ")";
    } else if (ret < 0) {
        ret = "❌";
    } else {
        ret = "✅";
    }
    items.innerHTML = ret;
}
