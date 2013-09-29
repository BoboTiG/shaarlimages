<?php

class Rss
{

    /**
     * RSS cached page file name.
     */
    private $images = array();

    /**
     * RSS cached page file name.
     */
    private $filename = '';


    public function __construct($nb = 50) {
        $this->images = Fct::unserialise(Config::$database);
        if ( $nb == 'all' ) {
            Config::$number = count($this->images);
        } else {
            Config::$number = max(1, min(count($this->images), $nb + 0));
        }
        $this->filename = Config::$rss_dir.Fct::small_hash(Config::$number).'.xml';
        Fct::create_dir(Config::$rss_dir);
    }

    /**
    * Create RSS Feed
    * https://github.com/mknexen/shaarli-river/blob/master/includes/create_rss.php
    * Inspired from http://www.phpntips.com/xmlwriter-2009-06/
    */
    public function get_data()
    {
        if ( !$this->is_cached() ) {
            $images = array_slice($this->images, 0, Config::$number);
            $this->create_rss($images);
        }
        return $this->get_cached();
    }

    /**
    * Check if a RSS cached page exists.
    */
    private function is_cached() {
        return is_file($this->filename);
    }

    /**
    * Retrieve the cached RSS page.
    */
    private function get_cached() {
        return file_get_contents($this->filename);
    }

    /**
    * Create RSS Feed.
    * https://github.com/mknexen/shaarli-river/blob/master/includes/create_rss.php
    * Inspired from http://www.phpntips.com/xmlwriter-2009-06/
    */
    private function create_rss($entries)
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

        foreach ( $entries as $key => $entry )
        {
            list($width, $height, $type) = getimagesize(Config::$img_dir.$entry['link']);

            // item
            $xml->startElement('item');
            if ( $entry['nsfw'] ) {
                $xml->writeElement('title', '[NSFW] '.$entry['link']);
            } else {
                $xml->writeElement('title', $entry['link']);
            }

            //$xml->writeElement('guid', $entry['guid']);
            $xml->writeElement('guid', $entry['guid']);

            $xml->startElement('description');
            $xml->writeCData(
                '<a href="'.Config::$link.'/?i='.$key.'"><img src="'.Config::$link.'/'.Config::$thumb_dir.$entry['link'].'"/></a>'
            );
            $xml->endElement();
            $xml->writeElement('pubDate', date('r', $entry['date']));

            // category
            if ( $entry['nsfw'] ) {
                $xml->startElement('category');
                $xml->text('nsfw');
                $xml->endElement();
            }

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

}

?>
