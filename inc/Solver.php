<?php

/**
 * Simple class to manage images downloaders.
 * For example, from a imgur.com link, it will grab the direct link
 * to the image (plus several useful nformations).
 *
 * Each function have to return array('link' => null) on error.
 * Or an array with at least : type, width, height, nsfw, link
 * If the Api does not handle one of these, set it to NULL.
 */
class Solver
{

    /**
     * Domains sensed to be working
     * domain => function name
     */
    public static $domains = array(
        //~ 'cheezburger.com' => 'cheezburger',
        'flickr.com' => 'flickr',
        'secure.flickr.com' => 'flickr',
        'www.flickr.com' => 'flickr',
        'imgur.com' => 'imgur',
        'twitter.com' => 'twitter',
        'xkcd.com' => 'xkcd',
    );

    /**
     * Authorization token to use Cheezburger API (Client ID)
     */
    //~ public static $cheezburger_auth = 'c3b2b49be03aa3f22129579985c902c9';

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
        'jpg' => 2, 'jpeg' => 2, 'png' => 3
    );


    /**
     * cheezburger.com - https://developer.cheezburger.com/
     */
    //~ public static function cheezburger($link)
    //~ {
        //~ $token = self::_cheezburger_request_token();
        //~ if ( $token !== false ) {
            //~ $parts = explode('/', trim($link, '/'));
            //~ $url = 'https://api.cheezburger.com/v1/assets/%d?access_token=%s';
            //~ $url = sprintf($url, end($parts), $token);
            //~ $req = json_decode(Fct::load_url($url), true);
            //~ //Fct::__($req);
            //~ if ( !empty($req['items']) && $req['items'][0]['asset_type_id'] == 0 ) {
                //~ $max = $req['items'][0]['media'][0];
                //~ if ( $max['is_animated'] == 0 ) {
                    //~ $sensible = preg_match('/nsfw/', strtolower($req['items'][0]['title']));
                    //~ // Type is not defined, set it to 0, it will be guessed later in Update::read_feed()
                    //~ return array(
                        //~ 'type' => 0,
                        //~ 'width' => (int)$max['width'],
                        //~ 'height' => (int)$max['height'],
                        //~ 'nsfw' => (bool)$sensible,
                        //~ 'link' => (string)$max['url']
                    //~ );
                //~ }
            //~ }
        //~ }
        //~ return array('link' => null);
    //~ }
    //~ 
    //~ private static function _cheezburger_request_token()
    //~ {
        //~ $url =
            //~ 'https://api.cheezburger.com/oauth/authorize?client_id='.self::$cheezburger_auth.
            //~ '&response_type=token&redirect_uri=https://api.cheezburger.com/oauth/login_success';
        //~ list($data, $location) = Fct::load_url($url, Fct::LOCATION);
        //~ Fct::__($data);
        //~ Fct::__($location);
        //~ return false;
    //~ }


    /**
     * flickr.com - https://secure.flickr.com/services/api/
     */
    public static function flickr($link)
    {
        if ( preg_match('/\d+/', $link, $parts) !== false ) {
            $url = 'https://api.flickr.com/services/rest/?method=flickr.photos.getSizes&format=php_serial&api_key=%s&photo_id=%s';
            $url = sprintf($url, self::$flickr_auth, $parts[0]);
            $req = unserialize(Fct::load_url($url));
            //Fct::__($req);
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
        }
        return array('link' => null);
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
            //Fct::__($req);
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
        return array('link' => null);
    }


    /**
     * twitter.com - https://dev.twitter.com/docs/api/1.1
     */
    public static function twitter($link)
    {
        if ( preg_match('#/photo/#', $link) ) {
            $url = $link.'/large';
            libxml_use_internal_errors(true);
            $doc = new DOMDocument();
            $doc->loadHTML(Fct::load_url($url));
            foreach ( $doc->getElementsByTagName('img') as $image ) {
                $src = $image->getAttribute('src');
                if ( substr($src, -6) == ':large' ) {
                    $img = substr($src, 0, -6);
                    $ext = strtolower(pathinfo($img, 4));
                    return array(
                        'type' => self::$ext[$ext],
                        'width' => (int)$image->getAttribute('width'),
                        'height' => (int)$image->getAttribute('height'),
                        'nsfw' => false,
                        'link' => $src
                    );
                }
            }
        }
        return array('link' => null);
    }


    /**
     * xkcd.com - https://xkcd.com/json.html
     */
    public static function xkcd($link)
    {
        $parts = explode('/', trim($link, '/'));
        $url = 'https://xkcd.com/'.end($parts).'/info.0.json';
        $req = json_decode(Fct::load_url($url), true);
        //Fct::__($req);
        if ( !empty($req['img']) ) {
            $parts = explode('/', $req['img']);
            $img = 'https://sslimgs.xkcd.com/comics/'.end($parts);
            return array(
                'type' => 0,
                'width' => 0,
                'height' => 0,
                'nsfw' => false,
                'link' => $img
            );
        }
        return array('link' => null);
    }

}

?>
