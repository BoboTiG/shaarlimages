<?php

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
    global $GLOBALS;
    list($width, $height, $type) = getimagesize($GLOBALS['config']['dir'].$file);
    if ( $type == 2 ) {  // jpeg
        $img = imagecreatefromjpeg($GLOBALS['config']['dir'].$file);
    } elseif ( $type == 3 ) {  // png
        $img = imagecreatefrompng($GLOBALS['config']['dir'].$file);
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

function bdd_save() {
    global $GLOBALS;
    file_put_contents($GLOBALS['config']['bdd_file'], serialise($GLOBALS['config']['bdd']));
}

function link_seems_ok($link) {
    // Firsts checks for a given link.
    global $GLOBALS;
    
    if ( substr($link, -1) == '/' ) { return false; }
     
    $parts = explode('/', $link);
    if ( in_array($parts[2], $GLOBALS['config']['not_domain']) ) { return false; }
    
    $ext = strtolower(pathinfo($link, 4));
    if ( !in_array($ext, $GLOBALS['config']['ext_ok']) ) { return false; }
    
    return true;
}

function test_link($link) {
    // Check the first 4 bytes of a given link ti check if it seems to be an image.

    $bytes = retieve_partial($link);
    if ( $bytes === false ) { return true; }
    
    $bytes = bin2hex($bytes);
    $ret = false;
    if ( substr($bytes, 0, 4) == 'ffd8' ) {  // jpeg
        //__('JPEG');
        $ret = true;
    }
    elseif ( substr($bytes, 0, 4) == '8950' ) {  // png
        //__('PNG');
        $ret = true;
    }
    
    return $ret;
}

function retieve_partial($link) {
    // Retrieve only the first 8 bytes opf a link
    if ( ($fp = fopen($link, 'rb')) ) {
        $bytes = fread($fp, 8);
        fclose($fp);
        return $bytes;
    }
    return false;
}

function retieve_partial0($link) {
    // Retrieve only the first 32 bytes opf a link
    // http://stackoverflow.com/questions/2032924/how-to-partially-download-a-remote-file-with-curl
    
    $writefn = function($ch, $chunk) {
        // Callback for retieve_partial() to ensure that only 32 bytes are downloaded.
        static $data = '';
        static $limit = 32;

        $len = strlen($data) + strlen($chunk);
        if ( $len >= $limit ) {
            $data .= substr($chunk, 0, $limit - strlen($data));
            __(strlen($data));
            __($data);
            return -1;
        }
        $data .= $chunk;
        return strlen($chunk);
    };

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $link);
    curl_setopt($ch, CURLOPT_RANGE, '0-32');
    curl_setopt($ch, CURLOPT_BINARYTRANSFER, 1);
    curl_setopt($ch, CURLOPT_WRITEFUNCTION, $writefn);  // ICI ça merde, dommage dommage.
    $result = curl_exec($ch);
    if ( $result === false ) {
        __(curl_error($ch));
        __(curl_errno($ch));
    }
    curl_close($ch);
    return $result;
}

function read_feed($url) {
    global $GLOBALS;
    $ret = 0;
    
    $last_up = 0;
    if ( !empty($GLOBALS['bdd']['updates'][$url]) ) {
        $last_up = $GLOBALS['bdd']['updates'][$url];
    }
    $now = date('U');
    if ( $now - $last_up < 60 * 60 * 24 ) { return $ret; }
    $GLOBALS['bdd']['updates'][$url] = $now;
    
    $feed = utf8_encode(@file_get_contents($url));
    if ( empty($feed) ) { return $ret; }
    
    try { $test = new SimpleXMLElement($feed); }
    catch (Exception $e) { return $ret; }
    
    foreach ( $test->channel->item as $item )
    {
        $pubDate = date('U', strtotime($item->pubDate));
        if ( $pubDate < $last_up ) { break; }
        
        // Strip URL parameters
        // http://stackoverflow.com/questions/1251582/beautiful-way-to-remove-get-variables-with-php/1251650#1251650
        $link = strtok((string)$item->link, '?');
        if ( link_seems_ok($link) && test_link($link) ) {
            if ( file_put_contents('.httmp', @file_get_contents($link)) ) {
                list($width, $height, $type) = getimagesize('.httmp');
                if ( $type == 2 || $type == 3 )  // jpeg, png
                {
                    $key = hash_hmac_file('adler32', '.httmp', 'bdd_key');
                    $img = pathinfo($item->link, PATHINFO_BASENAME);
                    if ( !pathinfo($img, 4) ) {
                        $img .= $GLOBALS['ext'][$type];
                    }
                    $filename = $key.'_'.$img;
                    if ( rename('.httmp', $GLOBALS['dir'].$filename) ) {
                        ++$ret;
                        $GLOBALS['bdd']['img'][$key]['date'] = (string)$pubDate;
                        $GLOBALS['bdd']['img'][$key]['orig'] = (string)$item->link;
                        $GLOBALS['bdd']['img'][$key]['link'] = (string)$filename;
                        $GLOBALS['bdd']['img'][$key]['guid'] = (string)$item->guid;
                        $GLOBALS['bdd']['img'][$key]['bg_color'] = (string)docolav($filename, $key);
                        $GLOBALS['bdd']['img'][$key]['nsfw'] = false;
                        // NSFW check, for sensible persons ... =]
                        if ( !empty($item->category) )
                        {
                            foreach ( $item->category as $category ) {
                                if ( strtolower($category) == 'nsfw' ) {
                                    $GLOBALS['bdd']['img'][$key]['nsfw'] = true;
                                    break;
                                }
                            }
                        }
                        if ( !$GLOBALS['bdd']['img'][$key]['nsfw'] ) {
                            $sensible = preg_match('/nsfw/', strtolower((string)$item->title.(string)$item->description));
                            $GLOBALS['bdd']['img'][$key]['nsfw'] = $sensible;
                        }
                    } else { unlink('.httmp'); }
                }
            }
        }
    }
    return $ret;
}

function get_opml() {
    global $GLOBALS;
    
    $mtime = 0;
    if ( is_file($GLOBALS['config']['shaarlis_opml']) ) {
        $stat = stat($GLOBALS['config']['shaarlis_opml']);
        $mtime = $stat['mtime'];
    }
    
    if ( date('U') - $mtime > 60 * 60 * 24 ) {
        file_put_contents($GLOBALS['config']['shaarlis_opml'], file_get_contents($GLOBALS['config']['shaarlis']));
    }
}

function get_feeds() {
    global $GLOBALS;
    get_opml();
    $feeds = array();
    $data = new SimpleXMLElement(file_get_contents($GLOBALS['config']['shaarlis_opml']), LIBXML_NOCDATA);
    foreach ( $data->body->outline as $shaarli ) {
        $feeds[] = (string)$shaarli->attributes()->xmlUrl;
    }
    return $feeds;
}



// -----------------------------------------------------------------------------------------------
// Simple cache system (mainly for the RSS/ATOM feeds).

class pageCache
{
    private $url; // Full URL of the page to cache (typically the value returned by pageUrl())
    private $shouldBeCached; // boolean: Should this url be cached ?
    private $filename; // Name of the cache file for this url

    /*
         $url = url (typically the value returned by pageUrl())
         $shouldBeCached = boolean. If false, the cache will be disabled.
    */
    public function __construct($url,$shouldBeCached)
    {
        $this->url = $url;
        $this->filename = $GLOBALS['config']['pagecache'].'/'.sha1($url).'.cache';
        $this->shouldBeCached = $shouldBeCached;
    }

    // If the page should be cached and a cached version exists,
    // returns the cached version (otherwise, return null).
    public function cachedVersion()
    {
        if (!$this->shouldBeCached) return null;
        if (is_file($this->filename)) {
            return file_get_contents($this->filename); exit; }
        return null;
    }

    // Put a page in the cache.
    public function cache($page)
    {
        if (!$this->shouldBeCached) return;
        if (!is_dir($GLOBALS['config']['pagecache'])) {
            mkdir($GLOBALS['config']['pagecache'],0705);
            chmod($GLOBALS['config']['pagecache'],0705); }
        file_put_contents($this->filename,$page);
    }

    // Purge the whole cache.
    // (call with pageCache::purgeCache())
    public static function purgeCache()
    {
        if (is_dir($GLOBALS['config']['pagecache']))
        {
            $handler = opendir($GLOBALS['config']['pagecache']);
            if ($handler!==false)
            {
                while (($filename = readdir($handler))!==false)
                {
                    if (endsWith($filename,'.cache')) { unlink($GLOBALS['config']['pagecache'].'/'.$filename); }
                }
                closedir($handler);
            }
        }
    }

}

/*  Converts a linkdate time (YYYYMMDD_HHMMSS) of an article to a RFC822 date.
    (used to build the pubDate attribute in RSS feed.)  */
function linkdate2rfc822($linkdate)
{
    return date('r',$linkdate); // 'r' is for RFC822 date format.
}

// ------------------------------------------------------------------------------------------
// Ouput the last N links in RSS 2.0 format.
function showRSS()
{
    header('Content-Type: application/rss+xml; charset=utf-8');

    // Cache system
    $query = $_SERVER["QUERY_STRING"];
    $cache = new pageCache(pageUrl(),startsWith($query,'do=rss'));
    $cached = $cache->cachedVersion(); if (!empty($cached)) { echo $cached; exit; }

    // If cached was not found (or not usable), then read the database and build the response:
    $LINKSDB=new linkdb(isLoggedIn() || $GLOBALS['config']['OPEN_SHAARLI']);  // Read links from database (and filter private links if used it not logged in).

    // Optionnaly filter the results:
    $linksToDisplay=array();
    if (!empty($_GET['searchterm'])) $linksToDisplay = $LINKSDB->filterFulltext($_GET['searchterm']);
    elseif (!empty($_GET['searchtags']))   $linksToDisplay = $LINKSDB->filterTags(trim($_GET['searchtags']));
    else $linksToDisplay = $LINKSDB;
    $nblinksToDisplay = !empty($_GET['nb']) ? max($_GET['nb'] + 0, 1) : 50;

    $pageaddr=htmlspecialchars(indexUrl());
    echo '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">';
    echo '<channel><title>'.htmlspecialchars($GLOBALS['title']).'</title><link>'.$pageaddr.'</link>';
    echo '<description>Shared links</description><language>en-en</language><copyright>'.$pageaddr.'</copyright>'."\n\n";
    if (!empty($GLOBALS['config']['PUBSUBHUB_URL']))
    {
        echo '<!-- PubSubHubbub Discovery -->';
        echo '<link rel="hub" href="'.htmlspecialchars($GLOBALS['config']['PUBSUBHUB_URL']).'" xmlns="http://www.w3.org/2005/Atom" />';
        echo '<link rel="self" href="'.htmlspecialchars($pageaddr).'?do=rss" xmlns="http://www.w3.org/2005/Atom" />';
        echo '<!-- End Of PubSubHubbub Discovery -->';
    }
    $i=0;
    $keys=array(); foreach($linksToDisplay as $key=>$value) { $keys[]=$key; }  // No, I can't use array_keys().
    while ($i<$nblinksToDisplay && $i<count($keys))
    {
        $link = $linksToDisplay[$keys[$i]];
        $guid = $pageaddr.'?'.smallHash($link['linkdate']);
        $rfc822date = linkdate2rfc822($link['linkdate']);
        $absurl = htmlspecialchars($link['url']);
        if (startsWith($absurl,'?')) $absurl=$pageaddr.$absurl;  // make permalink URL absolute
        if ($usepermalinks===true)
            echo '<item><title>'.htmlspecialchars($link['title']).'</title><guid isPermaLink="false">'.$guid.'</guid><link>'.$guid.'</link>';
        else
            echo '<item><title>'.htmlspecialchars($link['title']).'</title><guid isPermaLink="false">'.$guid.'</guid><link>'.$absurl.'</link>';
        if (!$GLOBALS['config']['HIDE_TIMESTAMPS'] || isLoggedIn()) echo '<pubDate>'.htmlspecialchars($rfc822date)."</pubDate>\n";
        if ($link['tags']!='') // Adding tags to each RSS entry (as mentioned in RSS specification)
        {
            foreach(explode(' ',$link['tags']) as $tag) { echo '<category domain="'.htmlspecialchars($pageaddr).'">'.htmlspecialchars($tag).'</category>'."\n"; }
        }

        // Add permalink in description
        $descriptionlink = '(<a href="'.$guid.'">Permalink</a>)';
        // If user wants permalinks first, put the final link in description
        if ($usepermalinks===true) $descriptionlink = '(<a href="'.$absurl.'">Link</a>)';
        if (strlen($link['description'])>0) $descriptionlink = '<br>'.$descriptionlink;
        echo '<description><![CDATA['.nl2br(keepMultipleSpaces(text2clickable(htmlspecialchars($link['description'])))).$descriptionlink.']]></description>'."\n</item>\n";
        $i++;
    }
    echo '</channel></rss><!-- Cached version of '.pageUrl().' -->';

    $cache->cache(ob_get_contents());
    ob_end_flush();
    exit;
}

// ------------------------------------------------------------------------------------------
// Ouput the last 50 links in ATOM format.
function showATOM()
{
    header('Content-Type: application/atom+xml; charset=utf-8');

    // $usepermalink : If true, use permalink instead of final link.
    // User just has to add 'permalink' in URL parameters. eg. http://mysite.com/shaarli/?do=atom&permalinks
    $usepermalinks = isset($_GET['permalinks']);

    // Cache system
    $query = $_SERVER["QUERY_STRING"];
    $cache = new pageCache(pageUrl(),startsWith($query,'do=atom') && !isLoggedIn());
    $cached = $cache->cachedVersion(); if (!empty($cached)) { echo $cached; exit; }
    // If cached was not found (or not usable), then read the database and build the response:

    $LINKSDB=new linkdb(isLoggedIn() || $GLOBALS['config']['OPEN_SHAARLI']);  // Read links from database (and filter private links if used it not logged in).


    // Optionnaly filter the results:
    $linksToDisplay=array();
    if (!empty($_GET['searchterm'])) $linksToDisplay = $LINKSDB->filterFulltext($_GET['searchterm']);
    elseif (!empty($_GET['searchtags']))   $linksToDisplay = $LINKSDB->filterTags(trim($_GET['searchtags']));
    else $linksToDisplay = $LINKSDB;
    $nblinksToDisplay = !empty($_GET['nb']) ? max($_GET['nb'] + 0, 1) : 50;

    $pageaddr=htmlspecialchars(indexUrl());
    $latestDate = '';
    $entries='';
    $i=0;
    $keys=array(); foreach($linksToDisplay as $key=>$value) { $keys[]=$key; }  // No, I can't use array_keys().
    while ($i<$nblinksToDisplay && $i<count($keys))
    {
        $link = $linksToDisplay[$keys[$i]];
        $guid = $pageaddr.'?'.smallHash($link['linkdate']);
        $iso8601date = linkdate2iso8601($link['linkdate']);
        $latestDate = max($latestDate,$iso8601date);
        $absurl = htmlspecialchars($link['url']);
        if (startsWith($absurl,'?')) $absurl=$pageaddr.$absurl;  // make permalink URL absolute
        $entries.='<entry><title>'.htmlspecialchars($link['title']).'</title>';
        if ($usepermalinks===true)
            $entries.='<link href="'.$guid.'" /><id>'.$guid.'</id>';
        else
            $entries.='<link href="'.$absurl.'" /><id>'.$guid.'</id>';
        if (!$GLOBALS['config']['HIDE_TIMESTAMPS'] || isLoggedIn()) $entries.='<updated>'.htmlspecialchars($iso8601date).'</updated>';

        // Add permalink in description
        $descriptionlink = htmlspecialchars('(<a href="'.$guid.'">Permalink</a>)');
        // If user wants permalinks first, put the final link in description
        if ($usepermalinks===true) $descriptionlink = htmlspecialchars('(<a href="'.$absurl.'">Link</a>)');
        if (strlen($link['description'])>0) $descriptionlink = '&lt;br&gt;'.$descriptionlink;

        $entries.='<content type="html">'.htmlspecialchars(nl2br(keepMultipleSpaces(text2clickable(htmlspecialchars($link['description']))))).$descriptionlink."</content>\n";
        if ($link['tags']!='') // Adding tags to each ATOM entry (as mentioned in ATOM specification)
        {
            foreach(explode(' ',$link['tags']) as $tag)
                { $entries.='<category scheme="'.htmlspecialchars($pageaddr,ENT_QUOTES).'" term="'.htmlspecialchars($tag,ENT_QUOTES).'" />'."\n"; }
        }
        $entries.="</entry>\n";
        $i++;
    }
    $feed='<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom">';
    $feed.='<title>'.htmlspecialchars($GLOBALS['title']).'</title>';
    if (!$GLOBALS['config']['HIDE_TIMESTAMPS'] || isLoggedIn()) $feed.='<updated>'.htmlspecialchars($latestDate).'</updated>';
    $feed.='<link rel="self" href="'.htmlspecialchars(serverUrl().$_SERVER["REQUEST_URI"]).'" />';
    if (!empty($GLOBALS['config']['PUBSUBHUB_URL']))
    {
        $feed.='<!-- PubSubHubbub Discovery -->';
        $feed.='<link rel="hub" href="'.htmlspecialchars($GLOBALS['config']['PUBSUBHUB_URL']).'" />';
        $feed.='<!-- End Of PubSubHubbub Discovery -->';
    }
    $feed.='<author><name>'.htmlspecialchars($pageaddr).'</name><uri>'.htmlspecialchars($pageaddr).'</uri></author>';
    $feed.='<id>'.htmlspecialchars($pageaddr).'</id>'."\n\n"; // Yes, I know I should use a real IRI (RFC3987), but the site URL will do.
    $feed.=$entries;
    $feed.='</feed><!-- Cached version of '.pageUrl().' -->';
    echo $feed;

    $cache->cache(ob_get_contents());
    ob_end_flush();
    exit;
}

?>
