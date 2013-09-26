<?php

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
     * Show debug informations.
     */
    public static $debug = true;

    /**
     * Bytes to download when using partial resource retrieval.
     */
    public static $bytes = 8;

    /**
     * User agent for resource retrieval.
     */
    public static $ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20130810 Firefox/17.0 Iceweasel/17.0.8';


    /**
     * Little debug function.
     */
    public static function __($value)
    {
        if ( self::$debug ) {
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
        curl_setopt($ch, CURLOPT_USERAGENT, self::$ua);
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

}

?>
