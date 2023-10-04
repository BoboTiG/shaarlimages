const loading = "<img src='/assets/img/loading.gif'/>";
const {title} = document;

function makeAllRequests() {
    "use strict";

    [...document.getElementsByTagName("tr")].forEach((tr, id, arr) => makeRequest(id));
}

function makeRequest(id) {
    "use strict";

    if (id === 0) {
        return;
    }

    let items = document.getElementById("feed-" + id);

    items.innerHTML  = loading;
    fetch("/update/" + id)
        .then((response) => {
            if (response.ok) {
                return response.json();
            }
            throw new Error("Something went wrong");
        })
        .then((data) => alertContents(data.count, id))
        .catch((error) => { alertContents(-1, id); });
}

function alertContents(itemsCount, id) {
    "use strict";

    let items = document.getElementById("feed-" + id);
    let sum = document.getElementById("sum");
    let response = "✅";

    if (itemsCount > 0) {
        sum.innerHTML = parseInt(sum.innerHTML, 10) + ret;
        document.title = "(" + sum.innerHTML + ") " + title;
        items.style.color = "green";
        response = "⭐ (+ " + itemsCount + ")";
    } else if (itemsCount < 0) {
        response = "❌";
    }
    items.innerHTML = response;
}
