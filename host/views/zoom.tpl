% this_site = site.copy()
% prefix = "[ ☂ NSFW ] " if "nsfw" in metadata["tags"] else ""
% this_site["title"] = f"{prefix}{metadata['link']} • {this_site['title']}"
% headers.append(f'<link rel="stylesheet" href="/assets/css/zoom.css?v={version}" />')
% headers.append('<meta property="og:title" content="' + this_site["title"] + '" />')
% headers.append('<meta property="og:type" content="website" />')
% headers.append('<meta property="og:url" content="' + this_site["url"] + '/zoom/' + metadata["link"] + '" />')
% headers.append('<meta property="og:image:url" content="' + this_site["url"] + '/thumbnail/' + metadata["link"] + '" />')
% headers.append('<meta property="og:description" content="' + this_site["description"] + '" />')
%include("header", site=this_site)

<div class="image-container-alone-toolbar">
    <a href="/" title="Retour à la galerie">🏠</a>
    <a href="/image/{{ metadata["link"] }}" title="Zoom" target="_blank">🔎</a>
    %if metadata["guid"].startswith("http"):
    <a href="{{ metadata["guid"] }}" title="Source" target="_blank">🔗</a>
    %end
</div>

<figure class="image-container-alone">
    <img src="/image/{{ metadata["link"] }}"{{!f' class="{css_class}"' if css_class else '' }} />
</figure>

%if metadata["tags"]:
<div id="tags">
    %for tag in metadata["tags"]:
    <a href="/search/tag/{{ tag }}">{{ tag }}</a>
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

window.onload = ambilightEffect;
</script>

%include("footer")
