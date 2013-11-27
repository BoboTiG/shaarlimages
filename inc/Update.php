<?php

include 'inc/Solver.php';

class Update
{

    /**
     * link_seems_ok() flags.
     */
    const BAD          = 0;  // Host is the same as the current one or a simple URL
    const GOOD_EXT     = 1;  // URL ends with an image extension
    const GOOD_SOLVER  = 2;  // Host is in the Solvers
    const SOLVER_DVA   = 3;  // host is *.deviantart.com
    const SOLVER_GUC   = 4;  // Host is *.googleusercontent.com
    const SOLVER_TUM   = 5;  // Host is *.tumblr.com
    const SOLVER_KON   = 6;  // Host is kuvaton.com

    /**
     * Shaarlis feed's URL.
     */
    public $feeds = array();


    public function __construct()
    {
        Fct::create_dir(Config::$img_dir);
        Fct::create_dir(Config::$thumb_dir);
        Fct::create_dir(Config::$data_dir);
        Fct::create_dir(Config::$cache_dir);
        self::get_opml(is_file(Config::$ompl_file));
    }

    /**
     * Retrieve the OPML file containing all shaarlis feed's.
     */
    private function get_opml($check_for_update = false)
    {
        $need_update = true;
        if ( $check_for_update )
        {
            $this->feeds = Fct::unserialise(Config::$ompl_file);
            $diff = date('U') - $this->feeds['update'];
            if ( $diff < Config::$ttl_opml ) {
                $need_update = false;
            }
        }
        if ( $need_update )
        {
            $data = json_decode(Fct::load_url(Config::$ompl_url), true);
            if ( !empty($data) )
            {
                foreach ( $data as $shaarli )
                {
                    $host = parse_url($shaarli['link'], 1);
                    $this->feeds['domains'][$host] = array(
                        'url' => stripslashes($shaarli['url'])
                    );
                }
                $this->feeds['update'] = date('U');
                Fct::secure_save(Config::$ompl_file, Fct::serialise($this->feeds));
            }
        }
    }

    /**
     * Retrieve images from one feed.
     */
    public function read_feed($domain)
    {
        if ( !isset($this->feeds['domains'][$domain]) ) {
            return false;
        }

        $ret = 0;
        $now = date('U');
        $images = array('date' => 0);
        $output = Config::$cache_dir.Fct::small_hash($domain).'.php';

        if ( is_file($output) ){
            $images = Fct::unserialise($output);
        }

        $feed = utf8_encode(Fct::load_url($this->get_url($domain)));
        if ( empty($feed) ) {
            return -1;
        }

        try {
            libxml_use_internal_errors(true);
            $test = new SimpleXMLElement($feed);
        } catch (Exception $e) {
            return -2;
        }

        $count = 0;
        if ( !empty($test->channel->item) ) foreach ( $test->channel->item as $item )
        {
            $pubDate = date('U', strtotime($item->pubDate));
            if ( $pubDate < $images['date'] ){
                break;
            }

            // Strip URL parameters
            // http://stackoverflow.com/questions/1251582/beautiful-way-to-remove-get-variables-with-php/1251650#1251650
            $link = strtok((string)$item->link, '?');

            $key = Fct::small_hash((string)$item->link);
            $host = parse_url($link, 1);
            $lflag = $this->link_seems_ok($host, $link);
            if (
                (empty($images[$key]) || (isset($images[$key]) && $pubDate < $images[$key]['date']))
                && $lflag > self::BAD
            ) {
                $data = false;
                $req = array();
                if ( $lflag >= self::GOOD_SOLVER ) {
                    switch ( $lflag ) {
                        case self::SOLVER_TUM: $host = 'tumblr.com'; break;
                        case self::SOLVER_DVA: $host = 'deviantart.com'; break;
                        case self::SOLVER_GUC: $host = 'googleusercontent.com'; break;
                    }
                    $func = Solver::$domains[$host];
                    $req = Solver::$func($link);
                    $link = $req['link'];
                }
                if ( ($data = Fct::load_url($link, Fct::IMAGE)) !== false ) {
                    list($width, $height, $type, $nsfw) = array(0, 0, 0, false);
                    if ( count($req) > 1 ) {
                        $link   = $req['link'];
                        $width  = $req['width'];
                        $height = $req['height'];
                        $type   = $req['type'];
                        $nsfw   = $req['nsfw'];
                    }
                    if ( $width == 0 || $height == 0 || $type == 0 ) {
                        list($width, $height, $type) = getimagesizefromstring($data);
                    }
                    if ( $type == 2 || $type == 3 )  // jpeg, png
                    {
                        $img = basename($link);
                        if ( $host == 'twitter.com' && substr($img, -6) == ':large' ) {
                            $img = substr($img, 0, -6);  // delete ':large'
                        }
                        if ( strlen(pathinfo($img, 4)) == 0 ) {
                            $img .= Config::$ext[$type];
                        }
                        $filename = $key.'_'.Fct::friendly_url($img);
                        if ( !is_file(Config::$img_dir.$filename) ) {
                            Fct::secure_save(Config::$img_dir.$filename, $data);
                            Fct::create_thumb($filename, $width, $height, $type);
                        }
                        $images[$key] = array();
                        $images[$key]['date']  = $pubDate;
                        $images[$key]['link']  = $filename;
                        $images[$key]['guid']  = (string)$item->guid;
                        $images[$key]['nsfw']  = $nsfw;
                        $images[$key]['title'] = utf8_decode((string)$item->title);
                        $images[$key]['desc']  = utf8_decode((string)$item->description);
                        $images[$key]['tags']  = array();
                        foreach ( $item->category as $category ) {
                            $images[$key]['tags'][] = utf8_decode(strtolower((string)$category));
                        }
                        // NSFW check, for sensible souls ... =]
                        if ( !$images[$key]['nsfw'] )
                        {
                            if ( in_array('nsfw', $images[$key]['tags']) ) {
                                $images[$key]['nsfw'] = true;
                            } elseif ( in_array(array('hentai', 'sexe', 'sexy'), $images[$key]['tags']) ) {
                                $images[$key]['nsfw'] = true;
                                $images[$key]['tags'][] = 'nsfw';
                            } elseif ( preg_match('/nsfw/', strtolower($images[$key]['title'].$images[$key]['desc'])) ) {
                                $images[$key]['nsfw'] = true;
                                $images[$key]['tags'][] = 'nsfw';
                            }
                        } elseif ( !in_array('nsfw', $images[$key]['tags']) ) {
                            $images[$key]['tags'][] = 'nsfw';
                        }
                        ++$ret;
                        if ( ++$count > 5 ) {
                            Fct::secure_save($output, Fct::serialise($images));
                            $count = 0;
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
     * Check a link.
     * Returns: check flags at the top of this file.
     */
    private function link_seems_ok($host, $link)
    {
        if ( $host == Config::$current_host )
            return self::BAD;
        if ( in_array(strtolower(pathinfo($link, 4)), Config::$ext_ok) ) {
            if ( $host == 'kuvaton.com' ) {
                return self::SOLVER_KON;
            }
            return self::GOOD_EXT;
        }
        if ( array_key_exists($host, Solver::$domains) )
            return self::GOOD_SOLVER;
        if ( substr($host, -10) == 'tumblr.com' )
            return self::SOLVER_TUM;
        if ( substr($host, -14) == 'deviantart.com' )
            return self::SOLVER_DVA;
        if ( substr($host, -21) == 'googleusercontent.com' )
            return self::SOLVER_GUC;
        return self::BAD;
    }

    /**
     * Getters.
     */
    public function get_feeds() {
        return $this->feeds['domains'];
    }

    public function get_url($domain) {
        return $this->feeds['domains'][$domain]['url']/*.'&nb=all'*/;
    }

}

?>
