/*
 * 
 * Galinear (Gallery using linear partition algorithm.
 * Version 0.1.
 * 
 * Tiger-222 https://tiger-222.fr
 * 
 * 
 * Changelog
 *  0.1 entirely JS/CSS/HTML (using JSON file)
 *  0.0 fisrt release
 */

var linearPartitionTable = function (seq, k) {
    'use strict';

    var i, j, x, n = seq.length,
        row = [],
        table = [],
        solution = [],
        listToMin = [],
        result = { computed: Infinity, value: Infinity };

    // Create the table
    for (i = 0; i < n; i += 1) {
        row = [];
        for (j = 0; j < k; j += 1) {
            row.push(0);
        }
        table.push(row);
    }

    // Create solution
    for (i = 0; i < n - 1; i += 1) {
        row = [];
        for (j = 0; j < k - 1; j += 1) {
            row.push(0);
        }
        solution.push(row);
    }

    for (i = 0; i < n; i += 1) {
        table[i][0] = seq[i] + (i ? table[i - 1][0] : 0);
    }

    for (i = 0; i < k; i += 1) {
        table[0][i] = seq[0];
    }

    for (i = 1; i < n; i += 1) {
        for (j = 1; j < k; j += 1) {
            listToMin = [];
            for (x = 0; x < i; x += 1) {
                listToMin.push([Math.max(table[x][j - 1], table[i][0] - table[x][0]), x]);
            }

            result = {
                computed: Infinity,
                value: Infinity
            };
            for (x = 0; x < i; x += 1) {
                if (listToMin[x][0] < result.computed) {
                    result = {
                        value: listToMin[x],
                        computed: listToMin[x][0]
                    };
                }
            }
            table[i][j] = result.value[0];
            solution[i - 1][j - 1] = result.value[1];
        }
    }
    return [table, solution];
};


var linearPartition = function (seq, k) {
    'use strict';

    var i, n = seq.length - 1, partitionTable, solution,
        ans = [], finalResult = [], partialAns = [];

    if (k < 1) {
        return finalResult;
    }
    if (k > n) {
        for (i = 0; i <= n; i += 1) {
            finalResult.push([seq[i]]);
        }
        return finalResult;
    }

    partitionTable = linearPartitionTable(seq, k);
    solution = partitionTable[1];

    k -= 2;
    while (k >= 0) {
        partialAns = [];
        for (i = solution[n - 1][k] + 1; i <= n; i += 1) {
            partialAns.push(seq[i]);
        }

        partialAns = [partialAns];
        ans = partialAns.concat(ans);
        n = solution[n - 1][k];
        k -= 1;
    }

    for (i = 0; i <= n; i += 1) {
        finalResult.push(seq[i]);
    }
    finalResult = [finalResult];

    return finalResult.concat(ans);
};

// options

/**

images = [{
    width:
    height:
    ... Custom info
}]

options = {
    containerWidth: int,
    preferedImageHeight: int,
    border: int,
    spacing: int
}

**/
var linearPartitionFitPics = function (images, options) {
    'use strict';

    options.border = options.border || 0;
    options.spacing = options.spacing || 0;

    var i, j, len, index = 0, summedWidth = 0, summedRatios = 0,
        partition, rows, row, rowWidth, image,
        weights = [], rowBuffer = [];

    for (i = 0, len = images.length; i < len; i += 1) {
        images[i].aspectRatio = images[i].width / images[i].height;
        summedWidth += images[i].aspectRatio * options.preferedImageHeight;
    }

    rows = Math.round(summedWidth / options.containerWidth);
    if ( rows > images.length ) {
        rows = images.length;
    }

    if (rows <= 1) {
        for (i = 0, len = images.length; i < len; i += 1) {
            images[i].width = parseInt(options.preferedImageHeight * images[i].aspectRatio, 10);
            images[i].height = options.preferedImageHeight;
        }
    } else {
        for (i = 0, len = images.length; i < len; i += 1) {
            weights.push(parseInt(images[i].aspectRatio * 100, 10));
        }

        partition = linearPartition(weights, rows);
        for (i in partition) {
            row = partition[i];
            rowWidth = options.containerWidth;
            summedRatios = 0;
            rowBuffer = [];
            len = row.length;

            if (options.spacing) {
                rowWidth -= options.spacing * (len - 1);
            }

            for (j = 0; j < len; j += 1) {
                rowBuffer.push(images[index]);
                index += 1;
            }

            for (j = 0, len = rowBuffer.length; j < len; j += 1) {
                summedRatios += rowBuffer[j].aspectRatio;
            }

            for (j = 0; j < len; j += 1) {
                image = rowBuffer[j];
                image.width = parseInt(rowWidth / summedRatios * image.aspectRatio, 10);
                image.height = parseInt(rowWidth / summedRatios, 10);
                if (j === len - 1) {
                    image.last = true;
                }
            }
        }
    }

    return images;
};


// Retrieve an array of URL parameters
var parse_query_string = function () {
    "use strict";
    var e = window.location.search,
        t = {};
    e.replace(new RegExp("([^?=&]+)(=([^&]*))?", "g"), function (e, n, r, i) {
        t[n] = i
    });
    return t
};

function addEvent(element, evnt, funct) {
    if (element.attachEvent) { 
        return element.attachEvent("on" + evnt, funct);
    } else {
        return element.addEventListener(evnt, funct, false);
    }
}

function get_infos(key) {
    "use strict";
    var i, len = gallery.length, ret = false;
    
    for (i= 0; i < len; i +=1) {
        if (gallery[i].key == key) {
            ret = gallery[i];
            if (!ret.docolav) {
                ret.docolav = "222";
            }
            break;
        }
    }
    return ret;
}

var params = parse_query_string();
if (params.i) {
    // Display one image
    var ix, iy,figure, a, img, title,
        x = document.documentElement.clientWidth,
        y = document.documentElement.clientHeight,
        image = get_infos(params.i);
    
    if (image === false) {
        document.write("<p>Aucune image ☹</p>");
    } else {
        title = image.src;
        if (image.nsfw) { title += " [ ☂ NSFW ]"; }
        document.title = title + " - " + document.title;
        
        img = document.createElement("img");
        img.className = "image-container-alone";
        img.width = image.w;
        img.height = image.h;
        img.src = galinear_opt["img_folder"] + image.src;
        
        a = document.createElement("a");
        a.href = "/";
        a.appendChild(img);
        
        figure = document.createElement("figure");
        figure.appendChild(a);
        document.body.appendChild(figure);
        document.body.style.background = "#" + image.docolav + " url('/assets/css/bg.png') repeat repeat";
        
        ix = img.offsetWidth;
        iy = img.offsetHeight;
        if (ix >= x || iy >= y) {
            if (ix >= x) {
                img.style.borderLeft = "none";
                img.style.borderRight = "none"
            }
            if (iy >= y) {
                img.style.borderTop = "none";
                img.style.borderBottom = "none"
            }
        }
    }
} else {
    // Display all images
    var gallery_images = [];

    linear_me = function () {
        "use strict";
        var i, image, nsfw, n = 0, page = 1, start = 0,
            len = gallery.length,
            container = document.getElementById("image-container"),
            max = Math.ceil(len / galinear_opt["per_page"]);
        
        if (params.p) {
            page = parseInt(params.p, 10);
            if (page < 0) { page = 0; }
            if (page > max) { page = max; }
            start = (page - 1) * galinear_opt["per_page"];
        }

        if (len === 0) {
            document.write("<p>Aucune image ☹</p>");
            return;
        }
        if (gallery_images.length === 0) {
            var figure, a, img;
            for (i = start; i < len && n < galinear_opt["per_page"]; i += 1, n += 1) {
                img = document.createElement("img");
                img.width = gallery[i].w;
                img.height = gallery[i].h;
                
                a = document.createElement("a");
                a.href = "?i=" + gallery[i].key;
                a.appendChild(img);
                if (gallery[i].nsfw && !galinear_opt["show_nsfw"]) {
                    nsfw = document.createElement("span");
                    a.className = "nsfw";
                    a.appendChild(nsfw);
                }
                
                figure = document.createElement("figure");
                figure.appendChild(a);
                container.appendChild(figure);
                
                gallery_images.push({
                    originalImage: container.getElementsByTagName("figure")[n].getElementsByTagName("img")[0],
                    width: gallery[i].w,
                    height: gallery[i].h
                });
            }
        }

        var resized_images = linearPartitionFitPics(gallery_images, {
                containerWidth: document.documentElement.clientWidth - 16,  // 8px * 2 from body margins
                preferedImageHeight: parseInt(document.documentElement.clientHeight / galinear_opt["lines"], 10),
                spacing: 4
            }),
            images = container.getElementsByTagName("figure");

        for (i = 0, len = gallery_images.length; i < len; i += 1) {
            image = gallery_images[i];
            image.originalImage.height = resized_images[i].height;
            image.originalImage.width = resized_images[i].width;
            
            // fonctionne pas
            addEvent(image.originalImage, "load", (function (i) {
                images[i].style.background = "inherit";
                image.originalImage.style.visibility = "visible";
            })(i));
            
            image.originalImage.src = galinear_opt["img_folder"] + gallery[start + i].src;
            if (!image.last) {
                images[i].style.marginRight = "4px";
            }
        }
        
        // Pagination
        if (!params.d) {
            var text = "", pagination = document.createElement("div");
            if ( page > 0 && page < max ) {
                text += '<a href="?p='+ (page + 1) + '">◄ Vieilleries</a> &nbsp; ';
            }
            text += ' &nbsp; page ' + page + '/' + max + ' &nbsp; ';
            if (page > 1) {
                text += ' &nbsp; <a href="?p='+ (page - 1) + '">Nouveautés ►</a>';
            }
            pagination.innerHTML = text;
            pagination.className = "pagination";
            container.appendChild(pagination);
        }
    };
    
    window.onload = linear_me;
    window.onresize = linear_me;
}
