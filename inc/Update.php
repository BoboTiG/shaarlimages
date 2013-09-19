<?php

include 'inc/Functions.php';

class Update
{

    /**
     * Folder containing images.
     */
    private $img_dir = 'images/';

    /**
     * Folder containing data.
     */
    private $data_dir = 'data/';

    /**
     * Cache folder.
     */
    private $cache_dir = 'data/cache/';

    /**
     * File where to save shaarlis feed's.
     */
    private $ompl_file = 'data/shaarlis.php';

    /**
     * Images database.
     */
    private $img_file = 'data/images.php';
    
    /**
     * Image database file.
     */
    private $database = 'data/images.php';

    /**
     * JSON file, generated from the images database.
     */
    private $json_file = 'images.json';

    /**
     * URL to the up to date shaarlis feed's.
     */
    private $ompl_url = 'http://shaarli.fr/opml?mod=opml';

    /**
     * Time to live for the OPML file.
     */
    private $ttl_opml = 86400;  // 60 * 60 * 24

    /**
     * Time to live for each shaarli.
     */
    private $ttl_shaarli = 21600;  // 60 * 60 * 6

    /**
     * Authorized extensions to download.
     */
    private $ext_ok = array('', 'jpg', 'png');

    /**
     * Extension to append if not present.
     * Key is the $type number of getimagesize().
     */
    private $ext = array(2 => '.jpg', 3 => '.png');

    /**
     * Shaarlis feed's URL.
     */
    public $feeds = array();


    public function __construct()
    {
        Fct::create_dir($this->img_dir, 0755);
        Fct::create_dir($this->data_dir);
        Fct::create_dir($this->cache_dir);
        self::get_opml(is_file($this->ompl_file));
    }

    /**
     * Retrieve the OPML file containing all shaarlis feed's.
     */
    private function get_opml($check_for_update = false)
    {
        $need_update = true;
        if ( $check_for_update )
        {
            $this->feeds = Fct::unserialise($this->ompl_file);
            $diff = date('U') - $this->feeds['update'];
            if ( $diff < $this->ttl_opml ) {
                $need_update = false;
            }
        }
        if ( $need_update )
        {
            $xml = Fct::load_url($this->ompl_url);
            if ( $xml !== false )
            {
                $data = new SimpleXMLElement($xml, LIBXML_NOCDATA);
                $now = date('U');
                foreach ( $data->body->outline as $shaarli )
                {
                    $url = (string)$shaarli->attributes()->xmlUrl;
                    $parts = explode('/', $url);
                    $this->feeds['domains'][$parts[2]] = array(
                        'url' => $url
                    );
                }
                $this->feeds['update'] = $now;
                Fct::secure_save($this->ompl_file, Fct::serialise($this->feeds));
            }
        }
    }

    /**
     * Retrieve images from one feed.
     */
    public function read_feed($domain) {
        if ( !isset($this->feeds['domains'][$domain]) ) {
            return false;
        }

        $ret = 0;
        $now = date('U');
        $images = array('date' => 0);
        $output = $this->cache_dir.Fct::small_hash($domain).'.php';

        if ( is_file($output) ){
            $images = Fct::unserialise($output);
        }
        if ( $now - $images['date'] < $this->ttl_shaarli ) {
            return $ret;
        }

        $feed = utf8_encode(Fct::load_url($this->get_url($domain)));
        if ( empty($feed) ) {
            return $ret - 1;
        }

        try {
            $test = new SimpleXMLElement($feed);
        } catch (Exception $e) {
            return $ret - 2;
        }

        foreach ( $test->channel->item as $item )
        {
            $pubDate = date('U', strtotime($item->pubDate));
            if ( $pubDate < $images['date'] ){
                break;
            }

            // Strip URL parameters
            // http://stackoverflow.com/questions/1251582/beautiful-way-to-remove-get-variables-with-php/1251650#1251650
            $link = strtok((string)$item->link, '?');

            if ( $this->link_seems_ok($domain, $link) && $this->test_link($link) ) {
                $data = Fct::load_url($link);
                if ( $data !== false )
                {
                    list($width, $height, $type) = getimagesizefromstring($data);
                    if ( $type == 2 || $type == 3 )  // jpeg, png
                    {
                        $key = Fct::small_hash($data);
                        if ( empty($images[$key]) )
                        {
                            $img = pathinfo($item->link, PATHINFO_BASENAME);
                            if ( !pathinfo($img, 4) ) {
                                $img .= $this->ext[$type];
                            }
                            $filename = Fct::friendly_url($img);
                            if ( Fct::secure_save($this->img_dir.$filename, $data) !== false ) {
                                ++$ret;
                                $images[$key] = array();
                                $images[$key]['date'] = $pubDate;
                                $images[$key]['link'] = $filename;
                                $images[$key]['guid'] = (string)$item->guid;
                                $images[$key]['docolav'] = $this->docolav($filename, $width, $height, $type);
                                $images[$key]['nsfw'] = false;
                                // NSFW check, for sensible persons ... =]
                                if ( !empty($item->category) )
                                {
                                    foreach ( $item->category as $category ) {
                                        if ( strtolower($category) == 'nsfw' )
                                        {
                                            $images[$key]['nsfw'] = true;
                                            break;
                                        }
                                    }
                                }
                                if ( !$images[$key]['nsfw'] )
                                {
                                    $sensible = preg_match('/nsfw/', strtolower((string)$item->title.(string)$item->description));
                                    $images[$key]['nsfw'] = $sensible;
                                }
                            }
                        }
                    }
                }
            }
        }
        $images['date'] = $now;
        Fct::secure_save($output, Fct::serialise($images));
        return $ret;
    }

    /**
     * Generate the JSON file.
     */
    public function generate_json() {
        if ( is_file($this->json_file) ) {
            $diff = date('U') - filemtime($this->json_file);
            if ( $diff < $this->ttl_shaarli ) {
                return;
            }
        }

        $images = array();
        $tmp = array();
        foreach ( glob($this->cache_dir.'*.php') as $db )
        {
            $tmp = Fct::unserialise($db);
            $tmp = array_splice($tmp, 1);  // Remove the 'date' key
            foreach ( array_keys($tmp) as $key )
            {
                if ( empty($images[$key]) ) {
                    $images[$key] = $tmp[$key];
                }
                elseif ( $tmp[$key]['date'] < $images[$key]['date'] ) {
                    // Older is better (could be the first to share)
                    $images[$key] = $tmp[$key];
                }
            }
        }
        uasort($images, 'self::compare_date');
        Fct::secure_save($this->database, Fct::serialise($images));

        $lines = "var gallery = [\n";
        $line = "{'key':'%s','src':'%s','w':%d,'h':%d,docolav:'%s','guid':'%s','date':%s,'nsfw':%d},\n";
        foreach ( $images as $key => $data )
        {
            list($width, $height, $type) = getimagesize($this->img_dir.$data['link']);
            $lines .= sprintf($line,
                $key, $data['link'],
                $width, $height,
                $data['docolav'],
                $data['guid'],
                $data['date'],
                $data['nsfw']
            );
        }
        $lines .= "];\n";
        Fct::secure_save($this->json_file, $lines);
    }
    
    private static function compare_date($a, $b)
    {
        if ( $a['date'] == $b['date'] ) {
            return 0;
        }
        return ( $a['date'] < $b['date'] ) ? 1 : -1;  // invert '1 : -1' for ASC
    }

    /**
     * Check a link syntax.
     * If it seems to be an image or does not finish by a slash, then it
     * seems okay.
     */
    private function link_seems_ok($domain, $link)
    {
        if ( substr($link, -1) == '/' ) {
            return false;
        }

        if ( !in_array(strtolower(pathinfo($link, 4)), $this->ext_ok) ) {
            return false;
        }

        return true;
    }

    /**
     * Retrieve the firsts bytes of a resource to check if it is an image.
     */
    private function test_link($link)
    {
        $ret = false;
        $bytes = Fct::load_url($link, true);
        if ( $bytes !== false )
        {
            $sig = substr(bin2hex($bytes), 0, 4);
            if ( $sig == 'ffd8' ) {  // jpeg
                $ret = true;
            }
            elseif ( $sig == '8950' ) {  // png
                $ret = true;
            }
        }
        return $ret;
    }

    /**
     * Compute the dominant color average.
     * http://stackoverflow.com/questions/6962814/average-of-rgb-color-of-image
     */
    private function docolav($file, $width, $height, $type)
    {
        if ( $type == 2 ) {  // jpeg
            $img = imagecreatefromjpeg($this->img_dir.$file);
        } elseif ( $type == 3 ) {  // png
            $img = imagecreatefrompng($this->img_dir.$file);
        } else {
            return '222';
        }

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

    /**
     * Getters.
     */
    public function get_feeds() {
        return $this->feeds['domains'];
    }

    public function get_url($domain) {
        return $this->feeds['domains'][$domain]['url'];
    }

}

?>
