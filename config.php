<?php

ini_set('memory_limit', '64M');
ini_set('display_errors', '1');
error_reporting(-1);

date_default_timezone_set('UTC');
$CONFIG = array();

$CONFIG['url'] = '/';
$CONFIG['dir'] = 'images/';
$CONFIG['bdd_file'] = $CONFIG['dir'].'images.db';
$CONFIG['bdd'] = array();
$CONFIG['show_nsfw'] = false;
$CONFIG['ext'] = array('jpeg', 'jpg', 'png');
$CONFIG['shaarlis'] = 'http://shaarli.fr/opml?mod=opml';



//
// FUNCTIONS - do not modify unless you know what you do.
//

if ( !is_dir($CONFIG['dir']) ) {
    mkdir($CONFIG['dir']);
}
elseif ( is_file($CONFIG['bdd_file']) ) {
    $CONFIG['bdd'] = unserialise(file_get_contents($CONFIG['bdd_file']));
}

// (un)Serialize functions
function serialise($value) {
    return base64_encode(gzdeflate(serialize($value)));
}
function unserialise($value) {
    $ret = unserialize(gzinflate(base64_decode($value)));
    if ( $ret === false ) {
        $ret = array();
    }
    return $ret;
}

// Get the dominant color average
function docolav($file, $key) {
    global $CONFIG;
    list($width, $height, $type) = getimagesize($CONFIG['dir'].$file);
    if ( $type == 2 ) {  // jpeg
        $img = imagecreatefromjpeg($CONFIG['dir'].$file);
    } elseif ( $type == 3 ) {  // png
        $img = imagecreatefrompng($CONFIG['dir'].$file);
    } else {
        return '222';
    }
    
    // http://stackoverflow.com/questions/6962814/average-of-rgb-color-of-image
    $tmp_img = ImageCreateTrueColor(1, 1);
    ImageCopyResampled($tmp_img, $img, 0, 0, 0, 0, 1, 1, $width, $height);
    $rgb = ImageColorAt($tmp_img, 0, 0);
    $r = ($rgb >> 16) & 0xFF;
    $g = ($rgb >> 8) & 0xFF;
    $b =  $rgb & 0xFF;
    unset($rgb);
    imagedestroy($tmp_img);
    imagedestroy($img);
    return sprintf('%02X%02X%02X', $r, $g, $b);
}

function __($value) {
    echo '<pre>';
    var_dump($value);
    echo '</pre>';
}
?>
