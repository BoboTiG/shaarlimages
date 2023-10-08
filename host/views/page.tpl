% headers.append(f'<link rel="stylesheet" href="/assets/css/page.css?v={version}" />')
%include("header")

<div id="top-bar">
    <div class="left">
        <input id="search" type="text" placeholder="Search" minlength="3" />
        <input id="search-tag" type="text" placeholder="Search by tag" minlength="1" />
        <button id="search-button">🔎</button>
    </div>
    <div class="right"><b>{{ total }}</b>&nbsp;images</div>
</div>

<div id="images-container"></div>

%if page > 0:
<footer>
    %if page > 1:
    <a href="/page/{{ page - 1 }}">⏮️</a> &nbsp;
    %end
    <b>{{ page }}</b> / {{ last }}
    % if page < last:
    &nbsp; <a href="/page/{{ page + 1 }}">⏭️</a>
    %end
</footer>
%end

<script src="/assets/js/galinear.js?v={{ version }}"></script>
<script>
%if page > 0:
// Keyboard left/right
document.onkeydown = (event) => {
    switch (event.key) {
        %if page > 1:
        case "ArrowLeft":
            document.location = "/page/{{ page - 1 }}";
            break;
        %end
        %if page < last:
        case "ArrowRight":
            document.location = "/page/{{ page + 1 }}";
            break;
        %end
    }
};
%end
window.onload = (event) => {
    // The gallery
    let container = document.getElementById("images-container");
    const images = [
        %for metadata in images:
        {src: "{{ metadata.link }}", width: {{ metadata.width }}, height: {{ metadata.height }}, docolav: "#{{ metadata.docolav }}", nsfw: {{ int("nsfw" in metadata.tags) }} },
        %end 
    ];
    const rows = linearPartition(images);
    
    rows.forEach((row, i) => {
        let div = document.createElement("div");
        div.classList.add("row");

        row.forEach((item, j) => {
            const index = rows.slice(0, i).reduce((prev, cur) => prev + cur.length, 0) + j;
            let a = document.createElement("a");
            let img = document.createElement("img");
            let image = images[index];

            a.href = "/zoom/" + image.src;
            a.style.width = item + "%";
            a.style.background = image.docolav;
            img.setAttribute("data-src", "/thumbnail/" + image.src);

            if (image.nsfw) {
                a.style.background += " url(/assets/img/nsfw.png) no-repeat top right";
                img.classList.add("nsfw");
            }

            a.appendChild(img);
            div.appendChild(a);
        });

        container.appendChild(div);
    });

    // Lazy loading
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const image = entry.target;

                image.src = image.dataset.src;
                image.onload = () => { image.classList.add("loaded") };

                imageObserver.unobserve(image);
            }
        });
    }, {
        rootMargin: "40px 0px 0px 0px",
        threshold: 0.01,
    });
    container.querySelectorAll("img").forEach(img => imageObserver.observe(img));

    // Search
    document.getElementById("search").onkeydown = (event) => {
        if (event.key === "Enter") {
            const search = document.getElementById("search");
            if (search.value && search.validity.valid) {
                document.location = "/search/" + search.value;
            }
        }
    };
    document.getElementById("search-tag").onkeydown = (event) => {
        if (event.key === "Enter") {
            const search = document.getElementById("search-tag");
            if (search.value) {
                document.location = "/search/tag/" + search.value;
            }
        }
    };
    document.getElementById("search-button").onclick = (event) => {
        const search_term = document.getElementById("search");
        const search_tag = document.getElementById("search-tag");

        if (search_term.value) {
            if (search_term.validity.valid) {
                document.location = "/search/" + search_term.value;
            }
        } else if (search_tag.value) {
            document.location = "/search/tag/" + search_tag.value;
        }
    };
};
</script>

%include("footer")
