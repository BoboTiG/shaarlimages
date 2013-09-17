<?php

/***********************************************************************
 * Database
 */
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
function bdd_save($which = 'lastup') {
    global $GLOBALS;
    if ( $which == 'lastup' ) {
        file_put_contents($GLOBALS['config']['lastup'], serialise($GLOBALS['updates']));
    } else {
        file_put_contents($GLOBALS['config']['bdd'], serialise($GLOBALS['images']));
    }
}
function __($value) {
    echo '<pre>'."\n";
    var_dump($value);
    echo '</pre>';
}

/***********************************************************************
 * Update
 */
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
    // Retrieve only the first 8 bytes of a link
    // http://stackoverflow.com/questions/2032924/how-to-partially-download-a-remote-file-with-curl
    global $GLOBALS;
    $parts = explode('/', $link);
    $referer = $parts[0].'//'.$parts[2];
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $link);
    curl_setopt($ch, CURLOPT_RANGE, '0-8');
    curl_setopt($ch, CURLOPT_BUFFERSIZE, 8);
    curl_setopt($ch, CURLOPT_USERAGENT, $GLOBALS['config']['ua']);
    curl_setopt($ch, CURLOPT_REFERER, $referer);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
    $result = curl_exec($ch);
    //~ if ( $result === false ) {
        //~ __(curl_error($ch));
        //~ __(curl_errno($ch));
    //~ }
    curl_close($ch);
    return $result;
}
function friendly_url($url) {
    return str_replace(' ', '-', filter_var(
        htmlentities(urldecode(trim($url)), ENT_QUOTES, 'UTF-8')
    , FILTER_SANITIZE_STRING));
}
function read_feed($url) {
    global $GLOBALS;
    $ret = 0;
    $last_up = 0;
    if ( !empty($GLOBALS['updates'][$url]) ) {
        $last_up = $GLOBALS['updates'][$url];
    }
    $now = date('U');
    if ( $now - $last_up < 60 * 60 * 24 ) { array($ret, array()); }
    $GLOBALS['updates'][$url] = $now;
    $context = stream_context_create(
        array(
            'http' => array(
                'header' => 'User-Agent: '.$GLOBALS['config']['ua']."\r\n"
            )
        )
    );
    $feed = utf8_encode(@file_get_contents($url, false, $context));
    if ( empty($feed) ) { return array(-1, array()); }
    try { $test = new SimpleXMLElement($feed); }
    catch (Exception $e) { return array(-1, array()); }
    $new_keys = array();
    foreach ( $test->channel->item as $item )
    {
        $pubDate = date('U', strtotime($item->pubDate));
        if ( $pubDate < $last_up ) { break; }
        // Strip URL parameters
        // http://stackoverflow.com/questions/1251582/beautiful-way-to-remove-get-variables-with-php/1251650#1251650
        $link = strtok((string)$item->link, '?');
        if ( link_seems_ok($link) && test_link($link) ) {
            if ( file_put_contents('.httmp', @file_get_contents($link, false, $context)) ) {
                list($width, $height, $type) = getimagesize('.httmp');
                if ( $type == 2 || $type == 3 )  // jpeg, png
                {
                    $key = hash_hmac_file('adler32', '.httmp', 'bdd_key');
                    $img = pathinfo($item->link, PATHINFO_BASENAME);
                    if ( !pathinfo($img, 4) ) {
                        $img .= $GLOBALS['config']['ext'][$type];
                    }
                    $filename = $key.'_'.friendly_url($img);
                    if ( rename('.httmp', $GLOBALS['config']['dir'].$filename) ) {
                        ++$ret;
                        $new_keys[] = $key;
                        $GLOBALS['images'][$key]['date'] = (string)$pubDate;
                        $GLOBALS['images'][$key]['link'] = $filename;
                        $GLOBALS['images'][$key]['guid'] = (string)$item->guid;
                        $GLOBALS['images'][$key]['docolav'] = (string)docolav($filename, $key);
                        $GLOBALS['images'][$key]['nsfw'] = false;
                        // NSFW check, for sensible persons ... =]
                        if ( !empty($item->category) )
                        {
                            foreach ( $item->category as $category ) {
                                if ( strtolower($category) == 'nsfw' ) {
                                    $GLOBALS['images'][$key]['nsfw'] = true;
                                    break;
                                }
                            }
                        }
                        if ( !$GLOBALS['images'][$key]['nsfw'] ) {
                            $sensible = preg_match('/nsfw/', strtolower((string)$item->title.(string)$item->description));
                            $GLOBALS['images'][$key]['nsfw'] = $sensible;
                        }
                    } else { unlink('.httmp'); }
                }
            }
        }
    }
    return array($ret, $new_keys);
}
function generate_json($new_keys) {
    $lines = '';
    if ( is_file($GLOBALS['config']['json']) ) {
        $fh = file($GLOBALS['config']['json']);
    } else {
        $fh = array("var gallery = [\n", "];\n");
    }
    $line = "    {'key':'%s','src':'%s','w':%d,'h':%d,docolav:'%s','guid':'%s','date':%s,'nsfw':%d},\n";
    $lines .= array_shift($fh);
    foreach ( $new_keys as $key ) {
        list($width, $height, $type) = getimagesize($GLOBALS['config']['dir'].$GLOBALS['images'][$key]['link']);
        $lines .= sprintf($line,
            $key, $GLOBALS['images'][$key]['link'],
            $width, $height,
            $GLOBALS['images'][$key]['docolav'],
            $GLOBALS['images'][$key]['guid'],
            $GLOBALS['images'][$key]['date'],
            $GLOBALS['images'][$key]['nsfw']
        );
    }
    $lines .= implode('', $fh);
    file_put_contents($GLOBALS['config']['json'], $lines);
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
?>
