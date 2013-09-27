<?php

/**
 * Useful functions (GD, sort, serailize, ...)
 */
class Fct
{

    /**
     * load_url() flags.
     */
    const NONE     = 0;  // Nothing special
    const PARTIAL  = 1;  // Retrieve only the firsts $bytes bytes

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
        if ( $flag == self::PARTIAL ) {
            curl_setopt($ch, CURLOPT_RANGE, '0-'.self::$bytes);
            curl_setopt($ch, CURLOPT_BUFFERSIZE, self::$bytes);
        }
        if ( !empty($headers) ) {
            curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        }
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_USERAGENT, Config::$ua);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        curl_setopt($ch, CURLOPT_SSLVERSION, 3);
        $data = curl_exec($ch);
        if ( curl_errno($ch) == 35 ) {
            curl_setopt($ch, CURLOPT_SSLVERSION, 2);
            $data = curl_exec($ch);
        }
        if ( $data === false ) {
            if ( curl_errno($ch) != 28 ) {  // timeout
                $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
                self::__($url.' -- '.curl_error($ch).' -- '.curl_errno($ch).' -- status code: '.$code);
            }
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
        if ( $ret === false ) {
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
        return str_replace(' ', '-', filter_var(
            htmlentities(
                stripslashes(strtok(urldecode(strtolower(trim($url))), '?'))
            , ENT_QUOTES, 'UTF-8')
        , FILTER_SANITIZE_STRING));
    }

    /**
     * Create a directory, if not present.
     */
    public static function create_dir($dir, $mode = 0750)
    {
        if ( !is_dir($dir) ) {
            mkdir($dir, 0750);
        }
    }

    /**
     * Returns the small hash of a string
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
        // Get rid of characters which need encoding in URLs.
        $hash = str_replace('+', '-', $hash);
        $hash = str_replace('/', '_', $hash);
        $hash = str_replace('=', '@', $hash);
        return $hash;
    }

    /**
     * Generate the JSON file.
     */
    public static function generate_json($force = true) {
        if ( !$force ) {
            if ( is_file(Config::$json_file) ) {
                $diff = date('U') - filemtime(Config::$json_file);
                if ( $diff < Config::$ttl_shaarli ) {
                    return;
                }
            }
        } else {
            usleep(1000000);  // 1 sec
        }

        $images = array();
        $tmp = array();
        foreach ( glob(Config::$cache_dir.'*.php') as $db )
        {
            $tmp = self::unserialise($db);
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
        self::secure_save(Config::$database, self::serialise($images));

        $lines = "var gallery = [\n";
        $line = "{'key':'%s','src':'%s','w':%d,'h':%d,docolav:'%s','guid':'%s','date':%s,'nsfw':%d},\n";
        foreach ( $images as $key => $data )
        {
            if ( is_file(Config::$img_dir.$data['link']) ) {
                list($width, $height, $type) = getimagesize(Config::$img_dir.$data['link']);
                if ( !is_file(Config::$thumb_dir.$data['link']) ) {
                    list($width, $height) = self::create_thumb($data['link'], $width, $height, $type);
                }
                $lines .= sprintf($line,
                    $key, $data['link'],
                    $width, $height,
                    $data['docolav'],
                    $data['guid'],
                    $data['date'],
                    $data['nsfw']
                );
            }
        }
        $lines .= "];\n";
        self::secure_save(Config::$json_file, $lines);
        self::invalidate_caches();
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
     * Compute the dominant color average.
     * http://stackoverflow.com/questions/6962814/average-of-rgb-color-of-image
     */
    public static function docolav($file, $width, $height, $type)
    {
        if ( $type == 2 ) {  // jpeg
            $img = imagecreatefromjpeg(Config::$img_dir.$file);
        } elseif ( $type == 3 ) {  // png
            $img = imagecreatefrompng(Config::$img_dir.$file);
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
     * Create an optimized and progressive JPEG small-szized file
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

        $thumb = imagecreatetruecolor($new_width, $new_height);
        imageinterlace($thumb, $progressive);
        imagecopyresized($thumb, $source, 0, 0, 0, 0, $new_width, $new_height, $width, $height);
        imagejpeg($thumb, Config::$thumb_dir.$file, $quality);

        chmod(Config::$thumb_dir.$file, 0644);

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

}

?>
