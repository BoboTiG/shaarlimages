<?php

ini_set('memory_limit', '64M');
ini_set('display_errors', '1');
error_reporting(-1);

date_default_timezone_set('UTC');
$GLOBALS = array();


//
// Here you can apply changes
//
$GLOBALS['config']['url'] = '/';
$GLOBALS['config']['pagecache'] = 'pagecache';
$GLOBALS['config']['dir'] = 'images/';
$GLOBALS['config']['json'] = 'images.json';
$GLOBALS['config']['shaarlis'] = 'http://shaarli.fr/opml?mod=opml';
$GLOBALS['config']['shaarlis_opml'] = '.shaarli.opml';
$GLOBALS['config']['bdd'] = $GLOBALS['config']['dir'].'.images.db';
$GLOBALS['config']['lastup'] = $GLOBALS['config']['shaarlis_opml'].'.db';
$GLOBALS['config']['ext'] = array(2 => '.jpg', 3 => '.png');
$GLOBALS['config']['ext_ok'] = array('', 'jpg', 'png');
$GLOBALS['config']['not_domain'] = array(
    'grooveshark.com',
    'soundcloud.com',
    'stackoverflow.com',
    'vimeo.com',
    'www.dailymotion.com',
    'www.youtube.com',
);
$GLOBALS['config']['domain_to_ckeck'] = array(
    'cheezburger.com' => "!<img class='event-item-lol-image' src='(.+)'!",
);
$GLOBALS['config']['ua'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20130810 Firefox/17.0 Iceweasel/17.0.8';
$GLOBALS['images'] = array();
$GLOBALS['updates'] = array();
//
// Not there ;)
//


include 'functions.php';
if ( !is_dir($GLOBALS['config']['dir']) ) {
    mkdir($GLOBALS['config']['dir']);
}
if ( !is_dir($GLOBALS['config']['pagecache']) ) {
    mkdir($GLOBALS['config']['pagecache']);
}
if ( is_file($GLOBALS['config']['bdd']) ) {
    $GLOBALS['images'] = unserialise(file_get_contents($GLOBALS['config']['bdd']));
}


?>
