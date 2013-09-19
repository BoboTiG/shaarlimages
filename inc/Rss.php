<?php

include 'inc/Functions.php';

class Rss
{

    /**
     * RSS title.
     */
    private $title = 'Shaarlimages';

    /**
     * RSS description.
     */
    private $description = 'Shaarlimages, la galerie des shaarlis !';

    /**
     * RSS link.
     */
    private $link = 'http://shaarlimages.net';

    /**
     * Folder containing images.
     */
    private $img_dir = 'images/';

    /**
     * Image database file.
     */
    private $database = 'data/images.php';

    /**
     * Folder containing pages cache.
     */
    private $rss_dir = 'data/rss/';

    /**
     * Images database.
     */
    private $number = 50;

    /**
     * Time to live for each shaarli. From inc/Update.php.
     */
    private $ttl_shaarli = 21600;  // 60 * 60 * 6

    /**
     * RSS cached page file name.
     */
    private $images = array();

    /**
     * RSS cached page file name.
     */
    private $filename = '';


    public function __construct($nb = 50) {
        $this->images = Fct::unserialise($this->database);
        $this->number = max(1, min(count($this->images), $nb));
        $this->filename = $this->rss_dir.Fct::small_hash($this->number);
        Fct::create_dir($this->rss_dir);
    }

    /**
    * Create RSS Feed
    * https://github.com/mknexen/shaarli-river/blob/master/includes/create_rss.php
    * Inspired from http://www.phpntips.com/xmlwriter-2009-06/
    */
    public function get_data()
    {
        if ( !$this->is_cached() ) {
            $images = array_slice($this->images, 0, $this->number);
            $this->create_rss($images);
        }
        return $this->get_cached();
    }

    /**
    * Check if a RSS cached page exists.
    */
    private function is_cached() {
        if ( is_file($this->filename) ) {
            $diff = date('U') - filemtime($this->filename);
            if ( $diff < $this->ttl_shaarli ) {
                return true;
            }
        }
        return false;
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

        //channel
        $xml->startElement('channel');

        // title, desc, link, date
        $xml->writeElement('title', $this->title);
        $xml->writeElement('description', $this->description);
        $xml->writeElement('link', $this->link);
        $xml->writeElement('pubDate', date('r'));

        foreach ( $entries as $key => $entry )
        {
            list($width, $height, $type) = getimagesize($this->img_dir.$entry['link']);

            // item
            $xml->startElement('item');
            if ( $entry['nsfw'] ) {
                $xml->writeElement('title', '[NSFW] '.$entry['link']);
            } else {
                $xml->writeElement('title', $entry['link']);
            }

            //$xml->writeElement('guid', $entry['guid']);
            $xml->writeElement('guid', $this->link.'/?i='.$key);

            $xml->startElement('description');
            $xml->writeCData(
                '<img src="'.$this->link.'/images/'.$entry['link'].'" width="'.$width.'" height="'.$height.'" />'
                .'<a href="'.$entry['guid'].'">Permalink</a>'
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
