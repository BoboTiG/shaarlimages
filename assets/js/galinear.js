/*
 *
 * Galinear (gallery using linear partition algorithm).
 * Version 0.3.
 *
 * Tiger-222  https://github.com/BoboTiG/galinear
 *
 *
 * Changelog:
 *
 *  0.3 - add ambilight effect (URL parameter 'al')
 *  0.2 - touch events ready!
 *      - filter by date is functional (URL parameter 'd': ?d=yyyymmdd)
 *      - use of thumbnails to speed up page load
 *      - better NSFW display
 *      - fix image border display
 *  0.1 - entirely JS/CSS/HTML (using JSON file)
 *      - better image loader (containers sized before images loading to
 *        resize all containers as desired)
 *      - few options can be change using URL parameters
 *      - add previous/next buttons
 *      - add a toolbar with links for each image
 *      - enable left/right keys for navigation in pages or images
 *  0.0 - first release
 */

var linearPartitionTable = function (seq, k) {
    'use strict';

    var i, j, x, len,
        n = seq.length,
        row = [],
        table = [],
        solution = [],
        listToMin = [],
        result = {};

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
            for (x = 0, len = listToMin.length; x < len; x += 1) {
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

    var i, solution, partitionTable,
        n = seq.length - 1,
        ans = [],
        finalResult = [],
        partialAns = [];

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

    var i, j, len, partition, rows, row, rowWidth, image,
        index = 0,
        summedWidth = 0,
        summedRatios = 0,
        weights = [],
        rowBuffer = [];

    for (i = 0, len = images.length; i < len; i += 1) {
        images[i].aspectRatio = images[i].width / images[i].height;
        summedWidth += images[i].aspectRatio * options.preferedImageHeight;
    }

    rows = Math.round(summedWidth / options.containerWidth);
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
                rowWidth -= (options.spacing * (len - 1));
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


// Ambilight effect
function makeLight() {
    // http://ketluts.net/zepixDemo/scripts/ambilight-image.js
    // http://chikuyonok.ru/2010/03/ambilight-video/
    'use strict';
    var left, right, all,
        img = document.getElementsByTagName('img')[0],
        grain = document.createElement('canvas'),
        grain_ctx = grain.getContext('2d'),
        mask = 'assets/img/mask.png',
        image = new Image(),
        block_width = 100,
        calcMidColor = function (data, from, to) {
            var i,
                result = [0, 0, 0],
                total_pixels = (to - from) / 4;

            for (i = from; i <= to; i += 4) {
                result[0] += data[i];
                result[1] += data[i + 1];
                result[2] += data[i + 2];
            }
            result[0] = Math.round(result[0] / total_pixels);
            result[1] = Math.round(result[1] / total_pixels);
            result[2] = Math.round(result[2] / total_pixels);
            return result;
        },
        getMidColors = function (canvas, ctx, block_width) {
            var i, from,
                width = canvas.width,
                height = canvas.height,
                lamps = 5,
                block_height = Math.ceil(height / lamps),
                pxl = block_width * block_height * 4,
                result = [],
                img_data = ctx.getImageData(0, 0, block_width, height),
                total = img_data.data.length;

            for (i = 0; i < lamps; i += 1) {
                from = i * width * block_width;
                result.push(calcMidColor(img_data.data, i * pxl, Math.min((i + 1) * pxl, total - 1)));
            }
            return result;
        },
        create_canvas = function (block_width, right)
        {
            var i, il, midcolors, grd,
                offsetx = block_width,
                canvas = document.createElement('canvas'),
                ctx = canvas.getContext('2d');

            canvas.style.position = 'absolute';
            canvas.style.top = '0';
            canvas.style.zIndex = '-2';
            canvas.style.width = '100%';  // Change to 50% for left/right
            canvas.style.height = '100%';
            canvas.width = block_width;
            canvas.height = img.height;
            if (right) {
                offsetx = img.width - block_width;
            }
            ctx.drawImage(img, offsetx, 0, canvas.width, canvas.height, 0, 0, canvas.width, canvas.height);
            midcolors = getMidColors(canvas, ctx, block_width),
            grd = ctx.createLinearGradient(0, 0, 0, canvas.height);
            for (i = 0, il = midcolors.length; i < il; i += 1) {
                grd.addColorStop(i / il, 'rgb(' + midcolors[i] + ')');
            }
            ctx.fillStyle = grd;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            return canvas;
        };

    // Left part
    //~ left = create_canvas(block_width, false);
    //~ left.style.left = '0';
    //~ document.body.appendChild(left);

    // Right part
    //~ right = create_canvas(block_width, true);
    //~ right.style.left = '50%';
    //~ document.body.appendChild(right);

    // Left & right parts at the same time, take block_width from left side
    all = create_canvas(block_width, false);
    all.style.left = '0';
    document.body.appendChild(all);

    // Grain
    grain.style.position = 'absolute';
    grain.style.top = '0';
    grain.style.left = '0';
    grain.style.zIndex = '-1';
    grain.style.width = '100%';
    grain.style.height = '100%';
    image.src = mask;
    grain.width = image.width;
    grain.height = image.height;
    grain_ctx.drawImage(image, 0, 0, grain.width, grain.height);
    document.body.appendChild(grain);
}

// Retrieve an array of URL parameters
var parse_query_string = function () {
    'use strict';
    var search = window.location.search,
        params = {};

    search.replace(new RegExp('([^?=&]+)(=([^&]*))?', 'g'), function ($0, $1, $2, $3) {
        params[$1] = $3;
    });
    return params;
};

function addEvent(element, evnt, funct) {
    'use strict';
    if (element.attachEvent) {
        return element.attachEvent('on' + evnt, funct);
    }
    return element.addEventListener(evnt, funct, false);
}

function curr_prev_next(key) {
    'use strict';
    var i,
        len = gallery.length,
        current = false,
        prev = false,
        next = false;

    for (i = 0; i < len; i += 1) {
        if (gallery[i].key === key) {
            current = gallery[i];
            if (i > 0) { prev = gallery[i - 1]; }
            if (i < len - 1) { next = gallery[i + 1]; }
            break;
        }
    }
    return {'current': current, 'previous': prev, 'next': next};
}

// From an epoch value, compute the yyyymmdd date.
function parse_date(value) {
    'use strict';
    var date = new Date(value * 1000),
        y = date.getFullYear().toString(),
        m = (date.getMonth() + 1).toString(),
        d = date.getDate().toString();

    if (m.length === 1) m = '0' + m;
    if (d.length === 1) d = '0' + d;
    return y + m + d;
}

var params = parse_query_string();
if (!galinear_opt) {
    // Default options
    // See https://github.com/BoboTiG/galinear for more informations.
    var galinear_opt = {
        'gallery_url': '/',
        'img_folder': 'images/',
        'thumb_folder': 'images/thumbs/',
        'per_page': 20,
        'lines': 3,
        'show_nsfw': 0,
        'toolbar': 1,
        'use_ambilight': 1,

        // Translations
        'txt_no_img': 'Aucune image ☹',
        'txt_older': '◄ Vieilleries',
        'txt_newer': 'Nouveautés ►',
        'txt_home': 'Retour à la galerie',
        'txt_permalink': 'Lien source',
        'txt_source': 'Image originale',

        // Other, do not touch
        'touch_support': 'ontouchend' in document,
    };
}


// URL parameters bypass
if (params.per_page) {
    galinear_opt.per_page = parseInt(params.per_page, 10);
    if (galinear_opt.per_page < 10) { galinear_opt.per_page = 10; }
}
if (params.lines) {
    galinear_opt.lines = parseInt(params.lines, 10);
    if (galinear_opt.lines < 2) { galinear_opt.lines = 2; }
}
if (params.show_nsfw) {
    galinear_opt.show_nsfw = parseInt(params.show_nsfw, 10);
    if (galinear_opt.show_nsfw !== 1) { galinear_opt.show_nsfw = 0; }
}
if (params.toolbar) {
    galinear_opt.toolbar = parseInt(params.toolbar, 10);
    if (galinear_opt.toolbar !== 1) { galinear_opt.toolbar = 0; }
}
if (params.al) {
    galinear_opt.use_ambilight = parseInt(params.al, 10);
    if (galinear_opt.use_ambilight !== 1) { galinear_opt.use_ambilight = 0; }
}

// Cookies parameters bypass (> URL > defaults options)
if (navigator.cookieEnabled && document.cookie.length > 0) {
    // FIX : à faire
}

if (params.i && gallery.length > 0) {
    // Display one image
    adjust_me = function (){
        'use strict';
        var fig = document.getElementsByClassName('image-container-alone')[0],
            img = fig.getElementsByTagName('img')[0];

        if (img.width < document.documentElement.clientWidth - 2) {
            img.style.borderLeft = '1px solid #111';
            img.style.borderRight = '1px solid #111';
        }
        if (img.height < document.documentElement.clientHeight - 2) {
            img.style.borderTop = '1px solid #111';
            img.style.borderBottom = '1px solid #111';
        }
        if (galinear_opt.use_ambilight) {
            makeLight();
        }
    };

    var figure, img, title, toolbar, home,
        permalink, source, previous, next,
        curr_prev_next_img = curr_prev_next(params.i),
        image = curr_prev_next_img.current,
        start = 0;;

    if (image === false) {
        document.write('<p>' + galinear_opt.txt_no_img + '</p>');
    } else {
        title = image.src;
        if (image.nsfw) { title += ' [ ☂ NSFW ]'; }
        title += ' - ' + document.title;
        document.title = title;

        if (!galinear_opt.use_ambilight) {
            if (!image.docolav) {
                image.docolav = '222';
            }
            document.body.style.background = '#' + image.docolav + ' url(assets/img/bg.png)';
            document.body.style.transition = '1s';
        }

        img = document.createElement('img');
        img.src = galinear_opt.img_folder + image.src;

        figure = document.createElement('figure');
        figure.className = 'image-container-alone';
        figure.appendChild(img);
        document.body.appendChild(figure);

        if (galinear_opt.touch_support) {
            // Use fingers :)
            addEvent(document, 'touchstart', function (e) {
                start = e.targetTouches[0].clientX;
            }, false);
            addEvent(document, 'touchmove', function (e) {
                e.preventDefault();
                if (start - e.targetTouches[0].clientX < 0) {
                    // Sliding to left
                    if (curr_prev_next_img.previous !== false) {
                        document.location = '?i=' + curr_prev_next_img.previous.key;
                    }
                } else {
                    // Sliding to right
                    if (curr_prev_next_img.next !== false) {
                        document.location = '?i=' + curr_prev_next_img.next.key;
                    }
                }
            }
            , false);
        } else {
            // Create the previous/next butons
            if (curr_prev_next_img.previous !== false) {
                previous = document.createElement('a');
                previous.className = 'image-container-previous';
                previous.href = '?i=' + curr_prev_next_img.previous.key;
                previous.text = '◄';
                document.body.appendChild(previous);
            }
            if (curr_prev_next_img.next !== false) {
                next = document.createElement('a');
                next.className = 'image-container-next';
                next.href = '?i=' + curr_prev_next_img.next.key;
                next.text = '►';
                document.body.appendChild(next);
            }

            // Keyboard left/right
            document.onkeydown = function(e) {
                e = e || window.event;
                switch (e.which || e.keyCode) {
                    case 37:
                        if (curr_prev_next_img.previous !== false) {
                            document.location = '?i=' + curr_prev_next_img.previous.key;
                        }
                        break;
                    case 39:
                        if (curr_prev_next_img.next !== false) {
                            document.location = '?i=' + curr_prev_next_img.next.key;
                        }
                        break;
                }
            };
        }

        // Create the toolbar
        if (galinear_opt.toolbar) {
            home = document.createElement('a');
            home.className = 'home';
            home.href = galinear_opt.gallery_url;
            home.title = galinear_opt.txt_home;

            permalink = document.createElement('a');
            permalink.className = 'permalink';
            if (image.guid) { permalink.href = image.guid; }
            permalink.title = galinear_opt.txt_permalink;

            source = document.createElement('a');
            source.className = 'source';
            source.href = img.src;
            source.title = galinear_opt.txt_source;

            toolbar = document.createElement('div');
            toolbar.className = 'image-container-alone-toolbar';
            toolbar.appendChild(home);
            toolbar.appendChild(permalink);
            toolbar.appendChild(source);

            document.body.appendChild(toolbar);
        }
    }

    window.onload = adjust_me;
    window.onresize = adjust_me;
} else {
    // Display all images
    var gallery_images = [];

    //~ fancy_load = function (tag_figure, tag_img) {
        //~ 'use strict';
        //~ tag_img.style.visibility = 'visible';
    //~ };

    linear_me = function () {
        'use strict';
        var i, image, images, figure, a, img, nsfw,
            pagination, resized_images, tmp, day,
            text = '',
            n = 0,
            page = 1,
            start = 0,
            len = gallery.length,
            container = document.getElementById('image-container'),
            max = Math.ceil(len / galinear_opt.per_page);

        if (params.p && !params.d) {
            page = parseInt(params.p, 10);
            if (page < 1) { page = 1; }
            if (page > max) { page = max; }
            start = (page - 1) * galinear_opt.per_page;
        }

        if (gallery_images.length === 0) {
            if (params.d) {
                // Filter by date
                tmp = [];
                for (i = 0; i < len; i += 1) {
                    if (parse_date(gallery[i].date) === params.d) {
                        tmp.push(gallery[i]);
                    }
                }
                gallery = tmp;
                len = gallery.length;
            }
            for (i = start; i < len && n < galinear_opt.per_page; i += 1, n += 1) {
                img = document.createElement('img');
                img.width = gallery[i].w;
                img.height = gallery[i].h;

                a = document.createElement('a');
                a.href = '?i=' + gallery[i].key;
                a.appendChild(img);

                figure = document.createElement('figure');
                figure.appendChild(a);

                // NSFW
                if (gallery[i].nsfw && !galinear_opt.show_nsfw) {
                    figure.className = 'nsfw';
                    figure.title = '/!\\ NSFW /!\\';
                }
                container.appendChild(figure);

                gallery_images.push({
                    originalImage: container.getElementsByTagName('figure')[n].getElementsByTagName('img')[0],
                    width: gallery[i].w,
                    height: gallery[i].h,
                    nsfw: gallery[i].nsfw
                });
            }
        }

        if (len === 0) {
            document.write('<p>' + galinear_opt.txt_no_img + '</p>');
            return;
        }

        resized_images = linearPartitionFitPics(gallery_images, {
            containerWidth: document.documentElement.clientWidth - 16,  // 8px * 2 from body margins
            preferedImageHeight: parseInt((document.documentElement.clientHeight - 25) / galinear_opt.lines, 10),
            spacing: 4
        });
        images = container.getElementsByTagName('figure');

        for (i = 0, len = gallery_images.length; i < len; i += 1) {
            image = gallery_images[i];
            image.originalImage.width = resized_images[i].width;
            image.originalImage.height = resized_images[i].height;

            // FIX : fonctionne pas
            //~ addEvent(image.originalImage, 'load', (fancy_load)(images[i], image.originalImage));

            // NSFW
            if (gallery_images[i].nsfw && !galinear_opt.show_nsfw) {
                figure = document.getElementsByTagName('figure')[i];
                if (resized_images[i].width < 95) {
                    figure.style.backgroundSize = 'contain';
                }
            }

            image.originalImage.src = galinear_opt.thumb_folder + gallery[start + i].src;
            if (!image.last) {
                images[i].style.marginRight = '4px';
            }
        }

        // Pagination
        if (!params.d) {
            pagination = document.createElement('div');
            if ( page > 0 && page < max ) {
                text += '<a href="?p='+ (page + 1) + '">' + galinear_opt.txt_older + '</a> &nbsp; ';
            }
            text += ' &nbsp; page ' + page + '/' + max + ' &nbsp; ';
            if (page > 1) {
                text += ' &nbsp; <a href="?p='+ (page - 1) + '">' + galinear_opt.txt_newer + '</a>';
            }
            pagination.innerHTML = text;
            pagination.className = 'pagination';
            container.appendChild(pagination);
        }

        if (!galinear_opt.touch_support) {
            // Keyboard left/right
            document.onkeydown = function(e) {
                e = e || window.event;
                switch (e.which || e.keyCode) {
                    case 37:
                        if ( page > 0 && page < max ) {
                            document.location = '?p=' + (page + 1);
                        }
                        break;
                    case 39:
                        if (page > 1) {
                             document.location = '?p=' + (page - 1);
                        }
                        break;
                }
            };
        }
    };

    window.onload = linear_me;
    window.onresize = linear_me;
}

