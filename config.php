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
$GLOBALS['config']['bdd_file'] = $GLOBALS['config']['dir'].'images.db';
$GLOBALS['config']['bdd'] = array();
$GLOBALS['config']['show_nsfw'] = false;
$GLOBALS['config']['shaarlis'] = 'http://shaarli.fr/opml?mod=opml';
$GLOBALS['config']['shaarlis_opml'] = '.shaarli.opml';
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
elseif ( is_file($GLOBALS['config']['bdd_file']) ) {
    $GLOBALS['bdd'] = unserialise(file_get_contents($GLOBALS['config']['bdd_file']));
}


?>
