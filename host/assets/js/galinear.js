/*
This is part of Shaarlimages.
Source: https://github.com/BoboTiG/shaarlimages
*/

function linearPartition(images) {
    // https://github.com/anotherempty/svelte-brick-gallery/blob/7fc5d87/src/lib/BrickGallery.svelte
    "use strict";

    const scaleWidth = (natWidth, natHeight, itemHeight) => {
        return Math.floor((itemHeight * natWidth) / natHeight);
    };
    const round = (n) => {
        const decimal = 4;
        return Math.round(n * Math.pow(10, decimal)) / Math.pow(10, decimal);
    };

    // Default height in pixel of an image
    const defaultItemHeight = 200;

    const containerWidth = document.documentElement.clientWidth;
    const itemsCount = images.length;

    let rows = [];
    let start = 0;
    let end = 0;
    let rowWidth = 0;
    let processedItems = 0;

    for (let i = 0; i < itemsCount; i++) {
        const currentWidth = Math.min(
            scaleWidth(images[i].width, images[i].height, defaultItemHeight),
            containerWidth
        );

        if (rowWidth + currentWidth > containerWidth) {
            // If current image doesn"t fit in the current row
            end = i;
            // Save current row to an array
            const row = new Array(end - start);

            // Share remaining space among images in current row
            const portion = (containerWidth - rowWidth) / (end - start);
            for (let j = start, k = 0; j < end; j++, k++) {
                const image = images[j];
                row[k] = round(
                    ((scaleWidth(image.width, image.height, defaultItemHeight) + portion) * 100) / containerWidth
                );
            }
            rows[rows.length] = row;
            processedItems += end - start;
            start = end;
            rowWidth = 0;
        }
        rowWidth += currentWidth;
    }

    // Add remaining images to last row
    const row = new Array(itemsCount - processedItems);
    for (let i = processedItems, j = 0; i < itemsCount; i++, j++) {
        row[j] = round(
            (scaleWidth(images[i].width, images[i].height, defaultItemHeight) * 100) / containerWidth
        );
    }

    rows[rows.length] = row;
    return rows;
}

function ambilightEffect() {
    // http://ketluts.net/zepixDemo/scripts/ambilight-image.js
    // http://chikuyonok.ru/2010/03/ambilight-video/
    "use strict";

    const calcMidColor = (data, from, to) => {
        "use strict";

        const totalPixels = (to - from) / 4;

        let result = [0, 0, 0];
        for (let i = from; i <= to; i += 4) {
            result[0] += data[i];
            result[1] += data[i + 1];
            result[2] += data[i + 2];
        }
        result[0] = Math.round(result[0] / totalPixels);
        result[1] = Math.round(result[1] / totalPixels);
        result[2] = Math.round(result[2] / totalPixels);

        return result;
    };
    const getMidColors = (canvas, ctx, blockWidth) => {
        "use strict";

        const {height} = canvas;
        const lamps = 5;
        const blockHeight = Math.ceil(height / lamps);
        const pxl = blockWidth * blockHeight * 4;
        const imgData = ctx.getImageData(0, 0, blockWidth, height).data;
        const total = imgData.length;

        let result = [];
        for (let i = 0; i < lamps; i += 1) {
            result.push(
                calcMidColor(imgData, i * pxl, Math.min((i + 1) * pxl, total - 1))
            );
        }

        return result;
    };
    const create_canvas = () => {
        "use strict";

        const img = document.getElementById("image");
        let canvas = document.createElement("canvas");
        let ctx = canvas.getContext("2d");

        canvas.style.position = "absolute";
        canvas.style.top = "0";
        canvas.style.zIndex = "-2";
        canvas.style.width = "100%";
        canvas.style.height = "100%";
        canvas.width = 128;
        canvas.height = img.height;
        ctx.drawImage(
            img,
            canvas.width,
            0,
            canvas.width,
            canvas.height,
            0,
            0,
            canvas.width,
            canvas.height
        );

        const midcolors = getMidColors(canvas, ctx, canvas.width);
        let gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        for (let i = 0, il = midcolors.length; i < il; i += 1) {
            gradient.addColorStop(i / il, "rgb(" + midcolors[i] + ")");
        }

        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        return canvas;
    };

    document.body.appendChild(create_canvas());
}
