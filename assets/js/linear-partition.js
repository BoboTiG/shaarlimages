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

var params = parse_query_string();
if (params.i) {
    var x = document.documentElement.clientWidth,
        y = document.documentElement.clientHeight,
        img = document.getElementsByTagName("figure")[0].getElementsByTagName("img")[0],
        ix = img.offsetWidth,
        iy = img.offsetHeight,
        need_change = ix >= x || iy >= y;
    if (need_change) {
        if (ix >= x) {
            img.style.borderLeft = "none";
            img.style.borderRight = "none"
        }
        if (iy >= y) {
            img.style.borderTop = "none";
            img.style.borderBottom = "none"
        }
    }
} else {
    linear_me = function () {
        "use strict";
        var e, t = document.getElementById("image-container").getElementsByTagName("figure"),
            n, r = t.length,
            i = [];
        if (i.length === 0) {
            var s = new Image;
            for (e = 0; e < r; e += 1) {
                s.src = t[e].getElementsByTagName("img")[0].src;
                i.push({
                    originalImage: t[e].getElementsByTagName("img")[0],
                    width: s.width,
                    height: s.height
                })
            }
        }
        var o = linearPartitionFitPics(i, {
            containerWidth: document.documentElement.clientWidth - 16,
            preferedImageHeight: parseInt(document.documentElement.clientHeight / 2, 10),
            spacing: 4
        });
        for (e = 0, r = i.length; e < r; e += 1) {
            n = i[e];
            n.originalImage.height = o[e].height;
            n.originalImage.width = o[e].width;
            if (!n.last) {
                t[e].style.marginRight = "4px"
            }
        }
    };
    window.onload = linear_me;
    window.onresize = linear_me
}
