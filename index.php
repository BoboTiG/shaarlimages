<?php

include 'config.php';

// One image to show?
$image =
    isset($_GET['i'])
    && file_exists($GLOBALS['config']['dir'].$_GET['i'])
    ? $_GET['i'] : NULL;

if ( $image !== NULL )
{
    $key = hash_hmac_file('adler32', $GLOBALS['config']['dir'].$image, 'bdd_key');
    if ( !empty($GLOBALS['bdd']['img'][$key]['bg_color']) ) {
        $GLOBALS['config']['bg_color'] = $GLOBALS['bdd']['img'][$key]['bg_color'];
    } else {
        $GLOBALS['bg_color'] = docolav($image, $key);
    }
}

?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Shaarlimages</title>
    <meta name="description" content="Shaarlimages, la galerie des shaarlis !">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="canonical" href="http://shaarlimages.net">
    <link rel="icon" type="image/png" href="/favicon.png" />
    <!--[if IE]>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <![endif]-->
<?php
    if ( $image === NULL ) {
        echo '<link rel="stylesheet" href="/assets/css/main.min.css">';
    } else {
        echo
        '<style>
            body {
                background: #'.$GLOBALS['config']['bg_color'].' url("/assets/css/bg.png") repeat repeat;
            }
            img {
                margin: auto; position: absolute;
                top: 0; left: 0; bottom: 0; right: 0;
                max-width: 100%; max-height: 100%;
                border: 1px solid #222;
                box-shadow: 0px 0px 20px #111;
            }
        </style>';
    }
?>
</head>
<body>

<!--
    Petit voyeur ;)
    Cette galerie d'image peut-être téléchargée et bidouillée :
        https://github.com/BoboTiG/shaarlimages
-->

<?php
    if ( $image === NULL ) {
        $images = !empty($GLOBALS['bdd']['img']) ? $GLOBALS['bdd']['img'] : array();
        
        if ( !empty($images) ) {
            // Date filter
            $use_date = false;
            if ( isset($_GET['d']) ) {
                $use_date = true;
                $date = date('U', strtotime($_GET['d']));
                $tmp = array();
                foreach ( $images as $img ) {
                    $pubDate = date('U', strtotime(date('Ymd', $img['date'])));
                    if ( $pubDate == $date ) {
                        $tmp[] = $img;
                    }
                }
                $images = $tmp;
            }
            rsort($images);
            
            // Page filter
            $nb = 20;
            $max = ceil(count($GLOBALS['bdd']['img']) / $nb);
            $page = 1;
            if ( isset($_GET['p']) ) {
                $page = min($max, max($page, $_GET['p'] + 0));
            }
            $i = ($page - 1) * $nb;
            $images = array_slice($images, $i, $nb);
            
            // Display
            if ( !empty($images) ) {
                echo '<div id="image-container">';
                foreach ( $images as $img ) {
                    printf('
                        <figure%s>
                            <a href="?i=%s"><img src="%s%s"></a>
                            <figcaption><a href="%s" title="Source">❄</a></figcaption>
                        </figure>',
                        ($img['nsfw'] && !$GLOBALS['config']['show_nsfw'] ? ' data="nsfw"' : ''),
                        urlencode($img['link']), $GLOBALS['config']['dir'], urlencode($img['link']),
                        $img['guid']);
                }
                echo '</div>';
                
                // Pagination
                if ( !$use_date ) {
                    echo '<footer>';
                    if ( $page > 0 && $page < $max ) {
                        printf('<a href="?p=%d">◄ Vieilleries</a> &nbsp; ', $page + 1);
                    }
                    printf(' &nbsp; page %d/%d &nbsp; ', $page, $max);
                    if ( $page > 1 ) {
                        printf(' &nbsp; <a href="?p=%d">Nouveautés ►</a>', $page - 1);
                    }
                    echo '</footer>';
                }
            } else { echo '<p>Aucune image ☹</p>'; }
        } else { echo '<p>Aucune image ☹</p>'; }
    }
    else {
        $return = isset($_SERVER['HTTP_REFERER']) ? $_SERVER['HTTP_REFERER'] : $GLOBALS['config']['url'];
        echo
        '<figure>
            <a href="'.$return.'"><img src="'.$GLOBALS['config']['dir'].urlencode($image).'"></a>
        </figure>';
    }
?>

<script async src="/assets/js/linear-partition.min.js"></script>

</body>
</html>
