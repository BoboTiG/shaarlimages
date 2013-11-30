<?php

ini_set('memory_limit', '512M');
ini_set('time_limit', 0);
ini_set('display_errors', 1);
error_reporting(-1);
date_default_timezone_set('UTC');


/**
 * Configuration class. You can edit all you want!
 */
class Config
{

    /**
     * Show debug informations.
     */
    public static $debug = true;

    /**
     * Host name running the galery -- to prevent re-downloading our images.
     */
    public static $current_host = 'shaarlimages.net';

    /**
     * RSS title.
     */
    public static $title = 'Shaarlimages';

    /**
     * RSS description.
     */
    public static $description = 'Shaarlimages, la galerie des shaarlis !';

    /**
     * RSS link.
     */
    public static $link = 'http://shaarlimages.net';

    /**
     * User agent for resource retrieval.
     */
    public static $ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20130810 Firefox/17.0 Iceweasel/17.0.8';

    /**
     * Time to live for the OPML file.
     */
    public static $ttl_opml = 21600;  // 60 * 60 * 6

    /**
     * Folder containing images.
     */
    public static $img_dir = 'images/';

    /**
     * Folder containing thumbnails.
     */
    public static $thumb_dir = 'images/thumbs/';

    /**
     * Folder containing data.
     */
    public static $data_dir = 'data/';

    /**
     * Cache folder.
     */
    public static $cache_dir = 'data/cache/';

    /**
     * File where to save shaarlis feed's.
     */
    public static $ompl_file = 'data/shaarlis.php';

    /**
     * Images database.
     */
    public static $img_file = 'data/images.php';

    /**
     * Image database file.
     */
    public static $database = 'data/images.php';

    /**
     * Folder containing pages cache.
     */
    public static $rss_dir = 'data/rss/';

    /**
     * JSON file, generated from the images database.
     */
    public static $json_file = 'images.json';

    /**
     * URL to the up to date shaarlis feed's.
     */
    public static $ompl_url = 'https://nexen.mkdir.fr/shaarli-api/feeds?pretty=1';

    /**
     * Authorized extensions to download.
     */
    public static $ext_ok = array('jpg', 'jpeg', 'png');

    /**
     * Extension to append if not present.
     * Key is the $type number of getimagesize().
     */
    public static $ext = array(2 => '.jpg', 3 => '.png');

    /**
     * Number of images to retrive into RSS feed.
     */
    public static $number = 50;

}

?>
