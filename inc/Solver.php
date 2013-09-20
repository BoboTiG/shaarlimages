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
        'imgur.com' => 'imgur'
    );

    /**
     * Authorization token to use Imgur API (Client-ID)
     */
    public static $imgur_auth = '578aa28d5b8bac5';

    /**
     * Authorized extensions
     */
    public static $ext = array('image/jpeg' => 2, 'image/png' => 3);


    /**
     * Imgur.com - http://api.imgur.com/
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
                    'width' => $req['data']['width'],
                    'height' => $req['data']['height'],
                    'nsfw' => (bool)$req['data']['nsfw'],
                    'link' => $req['data']['link']
                );
            }
        }
        return array('link' => $link);
    }

}

?>
