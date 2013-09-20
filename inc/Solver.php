<?php

/**
 * Simple class to manage images downloaders.
 * For example, from a imgur.com link, it will grab the direct link
 * to the image (plus several useful nformations).
 *
 * Each function have to return array('link' => $link) on error.
 * Or an array with at least : type, width, height, nsfw, link
 * If the Api does not handle one of these, set it to NULL.
 */
class Solver
{

    /**
     * Domains sensed to be working
     */
    public static $domains = array(
        // domain => function name
        'secure.flickr.com' => 'flickr',
        'flickr.com' => 'flickr',
        'imgur.com' => 'imgur',
    );

    /**
     * Authorization token to use flickr API (api_key)
     */
    public static $flickr_auth = 'bd2b16ff98f74d149709ac6f6d8de1cb';

    /**
     * Authorization token to use imgur API (Client-ID)
     */
    public static $imgur_auth = '578aa28d5b8bac5';

    /**
     * Authorized extensions
     */
    public static $ext = array(
        'image/jpeg' => 2, 'image/png' => 3,
        'jpg' => 2, 'png' => 3
    );


    /**
     * flickr.com - https://secure.flickr.com/services/api/
     */
    public static function flickr($link)
    {
        $parts = explode('/', trim($link, '/'));
        $url = 'https://api.flickr.com/services/rest/?method=flickr.photos.getSizes&format=php_serial&api_key=%s&photo_id=%s';
        $url = sprintf($url, self::$flickr_auth, end($parts));
        $req = unserialize(Fct::load_url($url));
        if ( $req['stat'] == 'ok' && $req['sizes']['candownload'] ) {
            $original = end($req['sizes']['size']);
            $ext = pathinfo($original['source'], 4);
            if ( array_key_exists($ext, self::$ext) ) {
                return array(
                    'type' => self::$ext[$ext],
                    'width' => (int)$original['width'],
                    'height' => (int)$original['height'],
                    'nsfw' => (bool)false,
                    'link' => (string)$original['source']
                );
            }
        }
        return array('link' => $link);
    }


    /**
     * imgur.com - http://api.imgur.com/
     */
    public static function imgur($link)
    {
        $parts = explode('/', $link);
        // Ignore albums
        if ( $parts[3] != 'a' ) {
            $headers = array('Authorization: Client-ID '.self::$imgur_auth);
            $url = 'https://api.imgur.com/3/image/'.end($parts);
            $req = json_decode(Fct::load_url($url, false, $headers), true);
            if ( $req['success'] && array_key_exists($req['data']['type'], self::$ext) ) {
                return array(
                    'type' => self::$ext[$req['data']['type']],
                    'width' => (int)$req['data']['width'],
                    'height' => (int)$req['data']['height'],
                    'nsfw' => (bool)$req['data']['nsfw'],
                    'link' => (string)$req['data']['link']
                );
            }
        }
        return array('link' => $link);
    }

}

?>
