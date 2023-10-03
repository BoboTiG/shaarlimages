%include("header")

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
document.onkeydown = function (e) {
    switch (e.code) {
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
window.onload = function () {
    // The gallery
    let container = document.getElementById("images-container");
    const images = [
        % # images is list([link, tags, width, height, docolav, feed])
        %for link, tags, width, height, docolav, _ in images:
        {"src": "{{ link }}", "width": {{ width }}, "height": {{ height }}, "docolav": "#{{ docolav }}"{{!', "class": "nsfw"' if "nsfw" in tags else '' }}},
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

            if (image.class) {
                a.classList.add(image.class);
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
};
</script>

%include("footer")
