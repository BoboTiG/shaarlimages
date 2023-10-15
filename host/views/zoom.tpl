% from types import SimpleNamespace
% this_site = SimpleNamespace(**vars(site) | {"title": metadata.title, "url": f"{site.url}/zoom/{metadata.link}"})
% headers.append(f'<link rel="stylesheet" href="/assets/css/zoom.css?v={version}" />')
% headers.append(f'<meta property="og:image" content="{site.url}/image/{metadata.link}" />')
% headers.append('<meta property="og:type" content="image" />')
% color_threshold = int(hex(255//2)[2:] * 3, 16)
% text_shadow = "#000" if int(metadata.docolav, 16) < color_threshold else "#fff"
% headers.append(f'<style>* {{ --docolav: #{metadata.docolav}; --txt-shadow: {text_shadow} }}</style>')
%include("header", site=this_site)

<div id="toolbar">
    <a href="/" title="Retour à la galerie">🏠</a>
    <a href="/random" title="Image aléatoire">🔀</a>
    <span>┈</span>
    <a href="/image/{{ metadata.link }}" title="Image en taille réelle" target="_blank">🖼️</a>
    %if metadata.guid.startswith("http"):
    <a href="{{ metadata.guid }}" title="Lien d'origine" target="_blank">🔗</a>
    %end
</div>

<figure>
    <img id="image" src="/image/{{ metadata.link }}"{{!f' class="{css_class}"' if css_class else '' }} />
</figure>

%if metadata.tags:
<div id="tags">
    %for tag in metadata.tags:
    <a onclick='document.location = "/search/tag/{{ tag }}"'>{{ !tag }}</a>
    %end
</div>
%end

<script src="/assets/js/galinear.js?v={{ version }}"></script>
<script>
// Keyboard left/right
document.onkeydown = function (e) {
    switch (e.code) {
        %if prev_img:
        case "ArrowLeft":
            document.location = "/zoom/{{ prev_img }}";
            break;
        %end
        %if next_img:
        case "ArrowRight":
            document.location = "/zoom/{{ next_img }}";
            break;
        %end
    }
};

// Swipe gestures
if ("ontouchend" in document) {
    document.ontouchstart = function (e) {
        start = e.targetTouches[0].clientX;
    };
    document.ontouchmove = function (e) {
        e.preventDefault();
        if (start - e.targetTouches[0].clientX < 0) {
            // Slide to the left
            %if prev_img:
            document.location = "/zoom/{{ prev_img }}";
            %end
        } else {
            // Slide to the right
            %if next_img:
            document.location = "/zoom/{{ next_img }}";
            %end
        }
    };
}

window.onload = () => {
    const adaptToolbar = () => {
        const image = document.getElementById("image");
        const toolbar = document.getElementById("toolbar");
        const toolbarRect = toolbar.getBoundingClientRect();
        const imageRect = image.getBoundingClientRect();

        if (imageRect.top < toolbarRect.bottom) {
            toolbar.classList.add("vertical");
        }
    };

    adaptToolbar();
    ambilightEffect();
}
</script>

%include("footer")
