<?php

/**
 * Useful functions (GD, sort, serialize, ...)
 */
class Fct
{

    /**
     * load_url() flags.
     */
    const NONE    = 0;  // Nothing special
    const PARTIAL = 1;  // Retrieve only the firsts $bytes bytes
    const IMAGE   = 2;  // We are retrieving an image

    /**
     * Prefix and suffix for data storage.
     */
    private static $prefix = '<?php /* ';
    private static $suffix = ' */ ?>';

    /**
     * Bytes to download when using partial resource retrieval.
     */
    private static $bytes = 8;


    /**
     * Little debug function.
     */
    public static function __($value)
    {
        if ( Config::$debug ) {
            echo '<pre>'."\n";
            var_dump($value);
            echo '</pre>'."\n\n";
        }
    }

    /**
     * Retrieve one resource entierely or partially.
     * http://stackoverflow.com/questions/2032924/how-to-partially-download-a-remote-file-with-curl
     */
    public static function load_url($url = null, $flag = self::NONE, $headers = array())
    {
        if ( $url === null ) {
            return false;
        }
        $ch = curl_init();
        switch ( $flag )
        {
            case self::PARTIAL:
                curl_setopt($ch, CURLOPT_RANGE, '0-'.self::$bytes);
                curl_setopt($ch, CURLOPT_BUFFERSIZE, self::$bytes);
                break;
            case self::IMAGE:
                curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 0);
                break;
            default:
                curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30);
                break;
        }
        if ( !empty($headers) ) {
            curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        }
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_USERAGENT, Config::$ua);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        curl_setopt($ch, CURLOPT_SSLVERSION, 3);
        $data = curl_exec($ch);
        if ( curl_errno($ch) == 35 ) {
            curl_setopt($ch, CURLOPT_SSLVERSION, 1);
            $data = curl_exec($ch);
        }
        curl_close($ch);
        return $data;
    }

    /**
     * Secure way to write a file.
     */
    public static function secure_save($file, $data)
    {
        $ret = file_put_contents($file, $data, LOCK_EX);
        if ( $ret ) {
            @chgrp($file, 'www-data');
            @chmod($file, 0775);
        } else {
            self::__(error_get_last());
        }
        return $ret;
    }

    /**
     * Custom serialize.
     */
    public static function serialise($value)
    {
        return self::$prefix
            .base64_encode(gzdeflate(serialize($value)))
            .self::$suffix;
    }

    /**
     * Custom unserialize.
     */
    public static function unserialise($file)
    {
        $ret = @unserialize(gzinflate(base64_decode(
            substr(
                file_get_contents($file, LOCK_EX),
                strlen(self::$prefix),
                -strlen(self::$suffix)
            )
        )));
        if ( $ret === false ) {
            self::__(error_get_last());
        }
        return $ret;
    }

    /**
     * Sanitize an URL.
     */
    public static function friendly_url($url)
    {
        $url = preg_replace('#\&([A-za-z])(?:acute|cedil|circ|grave|ring|tilde|uml)\;#', '\1', $url);
        $url = preg_replace('#\&([A-za-z]{2})(?:lig)\;#', '\1', $url);
        $url = stripslashes(strtok(urldecode(strtolower(trim($url))), '?'));
        filter_var(htmlentities($url, ENT_QUOTES, 'UTF-8'), FILTER_SANITIZE_STRING);
        if ( strlen($url) > 64 ) {
            $url = substr($url, strlen($url) - 64);
        }
        return str_replace(array(' ', '+', '%', '#', "'", '\\', '/'), '-', $url);
    }

    /**
     * Create a directory, if not present.
     */
    public static function create_dir($dir, $mode = 0777)
    {
        if ( !is_dir($dir) ) {
            mkdir($dir, $mode);
            @chgrp($file, 'www-data');
            @chmod($dir, $mode);
        }
    }

    /**
     * Returns the small hash of a string, using RFC 4648 base64url format
     * http://sebsauvage.net/wiki/doku.php?id=php:shaarli
     * eg. smallHash('20111006_131924') --> yZH23w
     * Small hashes:
     * - are unique (well, as unique as crc32, at last)
     * - are always 6 characters long.
     * - only use the following characters: a-z A-Z 0-9 - _ @
     * - are NOT cryptographically secure (they CAN be forged)
     *
     * @param string $text Text to convert into small hash
     *
     * @return string      Small hash corresponding to the given text
     */
    public static function small_hash($text)
    {
        $hash = rtrim(base64_encode(hash('crc32', $text, true)), '=');
        return strtr($hash, '+/', '-_');
    }

    /**
     * Generate the JSON file.
     * Added a RATIO limit for images with width/height too small or too big,
     * it prevents to have a gallery as beautiful as Internet Explorer ...
     */
    public static function generate_json($data = NULL, $output = NULL) {
        $images = array();

        if ( $data === NULL ) {
            foreach ( glob(Config::$cache_dir.'*.php') as $db )
            {
                $tmp = self::unserialise($db);
                if ( $tmp !== false ) {
                    unset($tmp['date']);
                    foreach ( array_keys($tmp) as $key )
                    {
                        if ( is_file(Config::$img_dir.$tmp[$key]['link']) ) {
                            /* RATIO limit */list($width, $height) = getimagesize(Config::$img_dir.$tmp[$key]['link']);
                            /* RATIO limit */if ( $height == 0 ) $height = 1;
                            /* RATIO limit */$ratio = $width / $height;
                            /* RATIO limit */if ( $ratio >= 0.3 && $ratio <= 3.0 )
                            /* RATIO limit */{
                                if ( empty($images[$key]) ) {
                                    $images[$key] = $tmp[$key];
                                }
                                elseif ( $tmp[$key]['date'] < $images[$key]['date'] ) {
                                    // Older is better (could be the first to share)
                                    $images[$key] = $tmp[$key];
                                }
                            /* RATIO limit */}
                        }
                    }
                }
            }
            uasort($images, 'self::compare_date');
            self::secure_save(Config::$database, self::serialise($images));
        } else {
            $images = $data;
        }

        $lines = "var gallery = [\n";
        $line = "{'k':'%s','s':'%s','w':%d,'h':%d,'g':'%s','d':%d,'n':%d},\n";
        foreach ( $images as $key => $data )
        {
            if ( is_file(Config::$img_dir.$data['link']) ) {
                list($width, $height, $type) = getimagesize(Config::$img_dir.$data['link']);
                if ( !is_file(Config::$thumb_dir.$data['link']) ) {
                    list($width, $height) = self::create_thumb($data['link'], $width, $height, $type);
                }
                if ( $width !== false && $height !== false ) {
                    $lines .= sprintf($line,
                        $key, $data['link'], $width, $height,
                        $data['guid'], $data['date'], $data['nsfw']
                    );
                }
            }
        }
        $lines .= "];\n";
        if ( $output === NULL ) {
            self::secure_save(Config::$json_file, $lines);
            self::invalidate_caches();
        } else {
            return $lines.'// Generated in '.$images[0]." sec\n";
        }
    }

    /**
     * Callback for uasort().
     * If will do a rsort() with a multi-dimensional array.
     */
    public static function compare_date($a, $b)
    {
        if ( $a['date'] == $b['date'] ) {
            return 0;
        }
        return ( $a['date'] < $b['date'] ) ? 1 : -1;  // invert '1 : -1' for sort()
    }

    /**
     * Create an optimized and progressive JPEG small-sized file
     * from original (big) image.
     */
    public static function create_thumb($file, $width, $height, $type)
    {
        $quality = 95;
        $progressive = true;

        // We want image 800x600 pixels max
        $coef = $width / $height;
        if ( $width >= $height ) {
            $new_width = ($width > 800) ? 800 : $width;
            $new_height = ceil($new_width / $coef);
        } else {
            $new_height = ($height > 600) ? 600 : $height;
            $new_width = ceil($new_height * $coef);
        }

        if ( $type == 2 ) {  // jpeg
            $source = imagecreatefromjpeg(Config::$img_dir.$file);
        } else {  // png
            $source = imagecreatefrompng(Config::$img_dir.$file);
        }
        if ( $source === false ) {
            return array(false, false);
        }

        $thumb = imagecreatetruecolor($new_width, $new_height);
        imageinterlace($thumb, $progressive);
        imagecopyresized($thumb, $source, 0, 0, 0, 0, $new_width, $new_height, $width, $height);
        imagejpeg($thumb, Config::$thumb_dir.$file, $quality);
        imagedestroy($source);
        imagedestroy($thumb);
        return array($new_width, $new_height);
    }

    /**
     * Invalidate all RSS caches.
     */
    public static function invalidate_caches()
    {
        array_map('unlink', glob(Config::$rss_dir.'*.xml'));
    }

    /**
     * Check 1: [Just in case, not really used]
     * Delete images which are in double in all the feeds.
     * As the hash is the image's URL, it could happen that 2 images are
     * the same, but their keys are differents.
     * So, we keep only the older.
     *
     * Check 2:
     * Delete unused images files and thumbnails.
     *
     * Return number of doubles and arrays of images files and thumbnails deleted.
     */
    public static function delete_doubles_and_unused()
    {
        $files = glob(Config::$img_dir.'*');
        unset($files[array_search('images/thumbs', $files)]);
        $thumb = glob(Config::$thumb_dir.'*');
        $I = array();
        $count = 0;

        foreach ( glob(Config::$cache_dir.'*.php') as $db )
        {
            $img = Fct::unserialise($db);
            unset($img['date']);

            // Check 1
            foreach ( $img as $key => $i ) {
                if ( isset($I[$key]) ) {
                    if ( $i['date'] < $I[$key]['date'] ) {
                        //~ $dbfile = Config::$cache_dir.$I[$key]['db'];
                        //~ $idb = Fct::unserialise($dbfile);
                        //~ unset($idb[$key]);
                        //~ Fct::secure_save($dbfile, Fct::serialise($idb));
                        $I[$key] = $i;
                        $I[$key]['db'] = $db;
                    }
                } else {
                    $I[$key] = $i;
                    $I[$key]['db'] = $db;
                }
                ++$count;
            }
        }
        $total = $count;
        $count -= count($I);

        // Check 2
        foreach ( $I as $img ) {
            $fname = $img['link'];
            if ( ($key = array_search(Config::$img_dir.$fname, $files)) !== false ) {
                unset($files[$key]);
            }
            if ( ($key = array_search(Config::$thumb_dir.$fname, $thumb)) !== false ) {
                unset($thumb[$key]);
            }
        }
        array_map('unlink', $files);
        array_map('unlink', $thumb);

        return array($total, $count, $files, $thumb);
    }

    /**
     * Search: look for a tag, term or both.
     */
    public static function look_for($value, $where = 'search')
    {
        $res = array(0);
        if ( strlen($value) < 2 ) {
            return $res;
        }

        $value = strtolower($value);
        $images = Fct::unserialise(Config::$img_file);
        $t1 = microtime(1);

        if ( $where == 'search' ) {
            foreach ( $images as $key => $img ) {
                if ( strpos(strtolower($img['guid'].$img['title'].$img['desc']), $value) !== false || in_array($value, $img['tags']) ) {
                    $res[$key] = $img;
                }
            }
        } elseif ( $where == 'searchtags' ) {
            foreach ( $images as $key => $img ) {
                if ( in_array($value, $img['tags']) ) {
                    $res[$key] = $img;
                }
            }
        } elseif ( $where == 'searchterms' ) {
            foreach ( $images as $key => $img ) {
                if ( strpos(strtolower($img['guid'].$img['title'].$img['desc']), $value) !== false ) {
                    $res[$key] = $img;
                }
            }
        }

        $res[0] = microtime(1) - $t1;
        return $res;
    }

}

?>
