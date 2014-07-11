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
        '9gag.com'              => 'neufgag',
        'www.9gag.com'          => 'neufgag',
        'www.bonjourmadame.fr'  => 'bonjourmadame',
        'i.chzbgr.com'          => 'cheezburger',
        'www.commitstrip.com'   => 'commitstrip',
        'deviantart.com'        => 'deviantart',
        'flickr.com'            => 'flickr',
        'secure.flickr.com'     => 'flickr',
        'www.flickr.com'        => 'flickr',
        'googleusercontent.com' => 'googleusercontent',
        'imgur.com'             => 'imgur',
        'kuvaton.com'           => 'kuvaton',
        'www.luc-damas.fr'      => 'luc',
        'tumblr.com'            => 'tumblr',
        'twitter.com'           => 'twitter',
        'xkcd.com'              => 'xkcd',
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
     * Authorization token to use imgur API (Client-ID)
     */
    public static $tumblr_auth = '5JSziBTlDIAxfLGV532QWZ7YpE87UhVa0ueoGfKHTQJMC0bkpi';

    /**
     * Authorized extensions
     */
    public static $ext = array(
        'image/gif'  => -1,
        'gif'        => -1,
        'image/jpeg' => 2,
        'jpg'        => 2,
        'jpeg'       => 2,
        'image/png'  => 3,
        'png'        => 3
    );


    /**
     * www.bonjourmadame.fr
     */
    public static function bonjourmadame($link)
    {
        $parts = explode('/', $link);
        if ( count($parts) < 4 ) {
            return array('link' => null);
        }
        $doc = Fct::load_xml($link);
        if ( $doc === false ) {
            return array('link' => null);
        }
        if ( $parts[3] == 'post' ) {
            foreach ( $doc->getElementsByTagName('meta') as $meta ) {
                if ( $meta->getAttribute('property') == 'og:image' ) {
                    return array(
                        'type'   => 0,
                        'width'  => 0,
                        'height' => 0,
                        'nsfw'   => true,
                        'link'   => $meta->getAttribute('content')
                    );
                }
            }
        } elseif ( $parts[3] == 'image' ) {
            $image = $doc
                ->getElementById('content')
                ->getElementsByTagName('img')
                ->item(0);
            return array(
                'type'   => 0,
                'width'  => 0,
                'height' => 0,
                'nsfw'   => true,
                'link'   => $image->getAttribute('data-src')
            );
        }
        return array('link' => null);
    }


    /**
     * cheezburger.com - https://developer.cheezburger.com/
     * Returns the link, as it is already an image, but URL ends with '/'.
     */
    public static function cheezburger($link)
    {
        return array('link' => $link);
    }


    /**
     * commitstrip.com - "Eux, ce sont de vrais codeurs !"
     */
    public static function commitstrip($link)
    {
        $doc = Fct::load_xml($link);
        if ( $doc === false ) {
            return array('link' => null);
        }
        $data = $doc->getElementsByTagName('article')->item(0);
        if ( is_null($data) ) {
            return array('link' => null);
        }
        $data = $data->getElementsByTagName('img');
        foreach ( $data as $img ) {
            $src = $img->getAttribute('src');
            if ( preg_match('/final/', $src) ) {
                $ext = pathinfo($src, 4);
                if ( array_key_exists($ext, self::$ext) ) {
                    return array(
                        'type'   => self::$ext[$ext],
                        'width'  => (int)$img->getAttribute('width'),
                        'height' => (int)$img->getAttribute('height'),
                        'nsfw'   => false,
                        'link'   => $src
                    );
                }
            }
        }
        return array('link' => null);
    }


    /**
     * deviantart.com - http://www.deviantart.com/developers/oembed
     */
    public static function deviantart($link)
    {
        if ( isset(self::$ext[pathinfo($link, 4)]) ) {
            return array('link' => $link);
        }
        $url = 'https://backend.deviantart.com/oembed?url='.$link;
        $req = json_decode(Fct::load_url($url), true);
        //~ Fct::__($req);
        if ( $req['type'] == 'photo' ) {
            $ext = pathinfo($req['url'], 4);
            if ( array_key_exists($ext, self::$ext) ) {
                $nsfw = isset($req['rating']) ? $req['rating'] == 'adult' : 0;
                return array(
                    'type'   => self::$ext[$ext],
                    'width'  => (int)$req['width'],
                    'height' => (int)$req['height'],
                    'nsfw'   => (bool)$nsfw,
                    'link'   => $req['url']
                );
            }
        }
        return array('link' => null);
    }


    /**
     * flickr.com - https://secure.flickr.com/services/api/
     */
    public static function flickr($link)
    {
        if ( preg_match('/\d+/', $link, $parts) ) {
            $url = 'https://api.flickr.com/services/rest/?method=flickr.photos.getSizes&format=php_serial&api_key=%s&photo_id=%s';
            $url = sprintf($url, self::$flickr_auth, $parts[0]);
            $req = unserialize(Fct::load_url($url));
            //~ Fct::__($req);
            if ( $req['stat'] == 'ok' && $req['sizes']['candownload'] ) {
                $original = end($req['sizes']['size']);
                $ext = pathinfo($original['source'], 4);
                if ( array_key_exists($ext, self::$ext) ) {
                    return array(
                        'type'   => self::$ext[$ext],
                        'width'  => (int)$original['width'],
                        'height' => (int)$original['height'],
                        'nsfw'   => false,
                        'link'   => (string)$original['source']
                    );
                }
            }
        }
        return array('link' => null);
    }


    /**
     * googleusercontent.com
     */
    public static function googleusercontent($link)
    {
        $bytes = Fct::load_url($link, Fct::PARTIAL);
        if ( $bytes !== false )
        {
            $ret = false;
            $sig = substr(bin2hex($bytes), 0, 4);
            if ( $sig == 'ffd8' ) {  // jpeg
                $ret = true;
            }
            elseif ( $sig == '8950' ) {  // png
                $ret = true;
            }
            if ( $ret === true ) {
                return array(
                    'type'   => 0,
                    'width'  => 0,
                    'height' => 0,
                    'nsfw'   => false,
                    'link'   => $link
                );
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
        if ( isset($parts[3]) && $parts[3] != 'a' ) {
            $headers = array('Authorization: Client-ID '.self::$imgur_auth);
            $url = 'https://api.imgur.com/3/image/'.end($parts);
            $req = json_decode(Fct::load_url($url, false, $headers), true);
            //~ Fct::__($req);
            if ( $req['success'] && $req['data']['section'] != 'pics' && array_key_exists($req['data']['type'], self::$ext) ) {
                return array(
                    'type'   => self::$ext[$req['data']['type']],
                    'width'  => (int)$req['data']['width'],
                    'height' => (int)$req['data']['height'],
                    'nsfw'   => (bool)$req['data']['nsfw'],
                    'link'   => (string)$req['data']['link']
                );
            }
        }
        return array('link' => null);
    }


    /**
     * kuvaton.com
     */
    public static function kuvaton($link)
    {
        $content = Fct::load_url($link);
        if ( preg_match('#src="(http://pics.kuvaton.com/.+)" alt=#', $content, $res) ) {
            return array(
                'type'   => 0,
                'width'  => 0,
                'height' => 0,
                'nsfw'   => false,
                'link'   => $res[1]
            );
        }
        return array('link' => null);
    }


    /**
     * www.luc-damas.fr - "Ça, c'est du prof !"
     */
    public static function luc($link)
    {
        $doc = Fct::load_xml($link);
        if ( $doc === false ) {
            return array('link' => null);
        }
        $image = $doc
            ->getElementById('content')
            ->getElementsByTagName('img')->item(0);
        $src = $image->getAttribute('src');
        $ext = strtolower(pathinfo($src, 4));
        return array(
            'type'   => self::$ext[$ext],
            'width'  => (int)$image->getAttribute('width'),
            'height' => (int)$image->getAttribute('height'),
            'nsfw'   => false,
            'link'   => $src
        );
        return array('link' => null);
    }


    /**
     * 9gag.com
     */
    public static function neufgag($link)
    {
        $doc = Fct::load_xml($link);
        if ( $doc === false ) {
            return array('link' => null);
        }
        foreach ( $doc->getElementsByTagName('link') as $meta ) {
            if ( $meta->getAttribute('rel') == 'image_src' ) {
                return array(
                    'type'   => 0,
                    'width'  => 0,
                    'height' => 0,
                    'nsfw'   => false,
                    'link'   => $meta->getAttribute('href')
                );
            }
        }
        return array('link' => null);
    }


    /**
     * tumblr.com - http://www.tumblr.com/docs/en/api/v2
     */
    public static function tumblr($link)
    {
        if ( preg_match('#image/(\d+)#', $link, $parts) ) {
            $url = sprintf('http://api.tumblr.com/v2/blog/derekg.org/posts?id=%d&api_key=%s', end($parts), self::$tumblr_auth);
            $req = json_decode(Fct::load_url($url), true);
            //~ Fct::__($req);
            if (
                $req['meta']['status'] == 200 &&
                $req['response']['total_posts'] == 1 &&
                $req['response']['posts'][0]['type'] == 'photo'
            ) {
                $nsfw = (bool)$req['response']['blog']['is_nsfw'];
                if ( !$nsfw ) {
                    foreach ( $req['response']['posts'][0]['tags'] as $tag ) {
                        if ( preg_match('/nsfw/', strtolower($tag)) ) {
                            $nsfw = true;
                            break;
                        }
                    }
                }
                $photo = $req['response']['posts'][0]['photos'][0]['original_size'];
                //~ Fct::__($photo);
                $ext = pathinfo($photo['url'], 4);
                if ( array_key_exists($ext, self::$ext) ) {
                    return array(
                        'type'   => self::$ext[$ext],
                        'width'  => (int)$photo['width'],
                        'height' => (int)$photo['height'],
                        'nsfw'   => $nsfw,
                        'link'   => $photo['url']
                    );
                }
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
            $doc = Fct::load_xml($url);
            if ( $doc === false ) {
                return array('link' => null);
            }
            foreach ( $doc->getElementsByTagName('img') as $image ) {
                $src = $image->getAttribute('src');
                if ( substr($src, -6) == ':large' ) {
                    $img = substr($src, 0, -6);
                    $ext = strtolower(pathinfo($img, 4));
                    return array(
                        'type'   => self::$ext[$ext],
                        'width'  => (int)$image->getAttribute('width'),
                        'height' => (int)$image->getAttribute('height'),
                        'nsfw'   => false,
                        'link'   => $src
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
        //~ Fct::__($req);
        if ( !empty($req['img']) ) {
            $parts = explode('/', $req['img']);
            $img = 'https://sslimgs.xkcd.com/comics/'.end($parts);
            return array(
                'type'   => 0,
                'width'  => 0,
                'height' => 0,
                'nsfw'   => false,
                'link'   => $img
            );
        }
        return array('link' => null);
    }

}

?>
