<?php

class Rss
{

    /**
     * Images database.
     */
    private $images = array();

    /**
     * RSS cached page file name.
     */
    private $filename = '';


    public function __construct($params = array())
    {
        Fct::create_dir(Config::$rss_dir);
        $this->images = Fct::unserialise(Config::$database);
        $this->filename = Config::$rss_dir.Fct::small_hash(Config::$number.implode('-', $params)).'.xml';
        $this->start = microtime(1);
        $this->version = 'Cached';
        if ( !is_file($this->filename) ) {
            $this->version = 'Generated';
            $this->filters($params);
            $this->images = array_slice($this->images, 0, Config::$number);
            $this->create_rss();
        }
    }

    /**
    * Few URL filters.
    */
    public function filters($params)
    {
        if ( !empty($params) ) {
            // Filter on tags
            if ( isset($params['tag']) )
            {
                $tags = array();
                foreach ( explode(',', strtolower($params['tag'])) as $tag ) {
                    $tags[$tag] = true;
                }
                foreach ( $this->images as $key => $entry ) {
                    $ok = false;
                    foreach ( $entry['tags'] as $tag ) {
                        if ( isset($tags[$tag]) ) {
                            $ok = true;
                            break;
                        }
                    }
                    if ( $ok === false ) {
                        unset($this->images[$key]);
                    }
                }
            }
            // Filter number of entries
            if ( isset($params['nb']) )
            {
                $nb = $params['nb'];
                if ( $nb == 'all' ) {
                    Config::$number = count($this->images);
                } else {
                    Config::$number = max(1, min(count($this->images), $nb + 0));
                }
            }
        }
    }

    /**
    * Create RSS Feed.
    * https://github.com/mknexen/shaarli-river/blob/master/includes/create_rss.php
    * Inspired from http://www.phpntips.com/xmlwriter-2009-06/
    */
    private function create_rss()
    {
        $xml = new XMLWriter();

        // Output directly to the cache file
        $xml->openURI($this->filename);
        $xml->startDocument('1.0');
        $xml->setIndent(2);
        //rss
        $xml->startElement('rss');
        $xml->writeAttribute('version', '2.0');
        $xml->writeAttribute('xmlns:atom', 'http://www.w3.org/2005/Atom');
        $xml->writeAttribute('xmlns:content', 'http://purl.org/rss/1.0/modules/content/');

        //channel
        $xml->startElement('channel');

        //rss
        $xml->startElement('atom:link');
        $xml->writeAttribute('href', Config::$link.'/?do=rss');
        $xml->writeAttribute('rel', 'self');
        $xml->writeAttribute('type', 'application/rss+xml');
        $xml->endElement();

        // title, desc, link, date
        $xml->writeElement('title', Config::$title);
        $xml->writeElement('description', Config::$description);
        $xml->writeElement('link', Config::$link);
        $xml->writeElement('pubDate', date('r'));

        foreach ( $this->images as $key => $entry )
        {
            // item
            $xml->startElement('item');
            if ( $entry['nsfw'] && !preg_match('/nsfw/', strtolower($entry['title'])) ) {
                $xml->writeElement('title', '[NSFW] '.$entry['title']);
            } else {
                $xml->writeElement('title', $entry['title']);
            }

            $xml->writeElement('guid', $entry['guid']);

            $xml->startElement('description');
            $xml->writeCData(
                '<a href="'.Config::$link.'/?i='.$key.'"><img src="'.Config::$link.'/'.Config::$thumb_dir.$entry['link'].'"/></a>'.
                '<p>'.$entry['desc'].'</p>'
            );
            $xml->endElement();
            $xml->writeElement('pubDate', date('r', $entry['date']));

            // category
            $xml->startElement('category');
            $xml->text(implode(', ', $entry['tags']));
            $xml->endElement();

            // end item
            $xml->endElement();
        }

        // end channel
        $xml->endElement();

        // end rss
        $xml->endElement();

        // end doc
        $xml->endDocument();

        // flush
        $xml->flush();
    }

    /**
    * Get RSS feed contents.
    */
    public function get_data()
    {
        $cached = '<!--'.$this->version.' version in '.(microtime(1) - $this->start).'-->'."\n";
        return file_get_contents($this->filename).$cached;
    }

}

?>
