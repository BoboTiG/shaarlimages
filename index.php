<?php
include 'config.php';

// One image to show?
$image =
    isset($_GET['i'])
    && file_exists($CONFIG['dir'].$_GET['i'])
    && in_array(strtolower(pathinfo($CONFIG['dir'].$_GET['i'], 4)), $CONFIG['ext'])
    ? $_GET['i'] : NULL;

if ( $image !== NULL )
{
    $key = hash_hmac_file('adler32', $CONFIG['dir'].$image, 'bdd_key');
    if ( !empty($CONFIG['bdd'][$key]['bg_color']) ) {
        $CONFIG['bg_color'] = $CONFIG['bdd'][$key]['bg_color'];
    } else {
        $CONFIG['bg_color'] = docolav($filename, $key);
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
                background: #'.$CONFIG['bg_color'].' url("/assets/css/bg.png") repeat repeat;
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
        $images = $CONFIG['bdd'];
        
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
        } else {
            rsort($images);
        }
        
        // Page filter
        $nb = 20;
        $max = round(count($CONFIG['bdd']) / $nb);
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
                        <figcaption><a href="%s" title="Permalink">❄</a></figcaption>
                    </figure>',
                    ($img['nsfw'] && !$CONFIG['show_nsfw'] ? ' data="nsfw"' : ''),
                    urlencode($img['link']), $CONFIG['dir'], urlencode($img['link']),
                    $img['guid']);
            }
            echo '</div>';
            
            // Pagination
            if ( !$use_date ) {
                echo '<footer>';
                if ( $page > 0 && $page < $max ) {
                    printf('<a href="?p=%d">◄ Older</a> &nbsp; ', $page + 1);
                }
                printf(' &nbsp; page %d/%d &nbsp; ', $page, $max);
                if ( $page > 1 ) {
                    printf(' &nbsp; <a href="?p=%d">Newer ►</a>', $page - 1);
                }
                echo '</footer>';
            }
        } else { echo '<p>No image found ☹</p>'; }
    }
    else {
        $return = isset($_SERVER['HTTP_REFERER']) ? $_SERVER['HTTP_REFERER'] : $CONFIG['url'];
        echo
        '<figure>
            <a href="'.$return.'"><img src="'.$CONFIG['dir'].$image.'"></a>
        </figure>';
    }
?>

<script async src="/assets/js/linear-partition.min.js"></script>

</body>
</html>
