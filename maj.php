<?php

include 'config.php';

if ( is_file($GLOBALS['config']['lastup']) ) {
    $GLOBALS['updates'] = unserialise(file_get_contents($GLOBALS['config']['lastup']));
}

$feeds = get_feeds();
$selected = !empty($_GET['u']) ? $_GET['u'] : NULL;

if ( in_array($selected, $feeds) ) {
    list($ret, $new_keys) = read_feed($selected);
    if ( $ret > 0 ) {
        bdd_save();
        generate_json($new_keys);
    } elseif ( $ret < 1 ) {
        bdd_save('lastup');
    }
    echo $ret;
    exit;
}

?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Shaarlimages - MàJ</title>
    <meta name="description" content="Shaarlimages, la galerie des shaarlis !">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/png" href="/favicon.png" />
    <style>
        body {
            background-color: #eee;
            text-shadow: 0px 0px 1px #fff;
        }
        table {
            width: 80%;
            margin: auto;
            border: 1px solid gray !important;
            border-collapse: collapse;
        }
        th {
            padding: 5px;
            color: #eee;
            background-color: #222;
            text-shadow: 0px 0px 1px #111;
        }
        td {
            padding: 5px;
            border-bottom: 1px solid gray;
        }
        a {
            outline: 0;
            display: inline-block;
            width: 40px;
            height: 40px;
            background: transparent url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAMAAAC7IEhfAAABEVBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoX7lMAAAAWnRSTlPpfD7+oizYU5gh4ze9EkhlcSbtjtktcs73MpFE+MZdDO7RnHdmtpQuIoRAEBf8eiqV4Yg7YvIGJKDWW/2XJUOD+3kp4PEKzRqGa/Ntfwgc6OwxD4reAQJcVQB3OGyDAAABL0lEQVR42s3Ud0vEQBAFcBV7PXtvZz0Ve8eC5YpXvJpcbr7/B/FNNmB2N4MLgvj+Gt7+CAnMpqvjmL+BbVdIbVcI6QYhf4TXPaUmWdKCe7fEUVKGY70Uy6cIF9/jLhCfOKJArhwoJ8GhkO28YlROgP4mu49wZifCS3b3aoYToV+Dm446OBEuwy1kHbZnCbDbZc3uAE9cICGefdpC3TAhJjdYS4Bn6CsmJN+GXOvvOI+mbrk62n4d8rIWLPiMdleHF4QcGm6dyycdem/o0gY8RVf14xAJ1PLEM8HVmrWPo1yXv7/ce+Fi1bPgUZGQmfHo5CBHSDGfcBX6VogzNXi8XXqoUpjZxMu13yI9w5PCda0UNNfMyj+AfGYjUlfn8r1WuRlIbc0Fjx0z/+zX/Dv4Bb5NHUFsNNkmAAAAAElFTkSuQmCC) no-repeat center center;
            opacity: .5;
        }
        a:hover {
            opacity: 1.0;
        }
        .tous {
            background-color: #999;
        }
        .num, .maj, .nouveautes {
            text-align: center;
            font-weight: bold;
        }
        .nouveautes {
            color: gray;
        }
        .center {
            text-align: center;
        }
        #sum {
            color: #000 !important;
        }
    </style>
</head>
<body>

<!-- Pré-chargement -->
<img src="/assets/css/loading.gif" style="display: none;">

<table>
    <tr>
        <th>N°</th>
        <th>Lien</th>
        <th>MàJ</th>
        <th>Nouveautés</th>
    </tr>
    <tr class="tous">
        <td colspan="2" class="center">Tous les shaarlis</td>
        <td class="maj"><a href="" onClick="makeAllRequests(); return false;" title="Mettre à jour tous les shaarlis."></a></td>
        <td class="nouveautes" id="sum"></td>
    </tr>
    <?php
        $i = 0;
        foreach ( $feeds as $feed ) {
            printf(
                '<tr>
                    <td class="num">%d</td>
                    <td>%s</td>
                    <td class="maj"><a href="" onClick=\'makeRequest("%s", %d); return false;\' title="Mettre à jour ce shaarli."></a></td>
                    <td class="nouveautes" id="%d"></td>
                </tr>',
                ++$i,
                $feed,
                $feed, $i,
                $i
            );
        }
        
    ?>
</table>

<script>

var sum = document.getElementById('sum');

function makeAllRequests() {
    var i, current, id = document.getElementsByTagName('tr'), len = id.length;
    sum.innerHTML = '0';
    for (i = 2; i < len; i += 1) {
        current = id[i].getElementsByTagName('td')[1].innerHTML;
        makeRequest(current, i - 1, true);
    }
}

function makeRequest(url, id, all = false) {
    var httpRequest = false, items = document.getElementById(id);
    items.innerHTML  = '<img src="/assets/css/loading.gif" alt="En cours..." title="En cours...">';
    if (window.XMLHttpRequest) {  // Mozilla, Safari, ...
        httpRequest = new XMLHttpRequest();
    }  else if (window.ActiveXObject) {  // IE
        try {
            httpRequest = new ActiveXObject('Msxml2.XMLHTTP');
        }
        catch (e) {
            try {
                httpRequest = new ActiveXObject('Microsoft.XMLHTTP');
            }
            catch (e) {}
        }
    }
    if (!httpRequest) { return false; }
    httpRequest.onreadystatechange = function() {
        alertContents(httpRequest, id, all);
    };
    httpRequest.open('GET', '?u=' + url, true);
    httpRequest.send(null);
}

function alertContents(httpRequest, id, all = false) {
    if (httpRequest.readyState == 4) {
        if (httpRequest.status == 200) {
            var ret = parseInt(httpRequest.responseText, 10),
                items = document.getElementById(id);
            items.style.color = 'gray';
            if (ret > 0) {
                if (all) {
                    sum.innerHTML = parseInt(sum.innerHTML, 10) + ret;
                }
                items.style.color = 'green';
                ret = '+ ' + ret;
            } else if (ret < 0 || isNaN(ret)) {
                console.log(ret);
                items.style.color = 'red';
                ret = 'Erreur';
                console.log(httpRequest.responseText);
            }
            items.innerHTML = ret;
        }
    }
}
</script>

</body>
</html>
