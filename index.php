<?php

if ( isset($_GET['error']) ) {
    header('Location: /index.php');
}

$do = !empty($_GET['do']) ? $_GET['do'] : NULL;
if ( $do !== NULL ) {
    if ( $do == 'rss' ) {
        include 'inc/Config.php';
        include 'inc/Functions.php';
        include 'inc/Rss.php';
        $rss = new RSS($_GET);
        echo $rss->get_data();
        exit;
    }
}

/*
 * Search:
 *  1) global   = ?search=VALUE
 *  2) in tags  = ?searchtags=VALUE
 *  3) in terms = ?searchterms=VALUE
 */
$search = !empty($_GET['search']) ? $_GET['search'] : NULL;
if ( $search !== NULL ) {
    $value = $search;
    $where = 'search';
} else {
    $search = !empty($_GET['searchtags']) ? $_GET['searchtags'] : NULL;
    if ( $search !== NULL ) {
        $value = $search;
        $where = 'searchtags';
    } else {
        $search = !empty($_GET['searchterms']) ? $_GET['searchterms'] : NULL;
        if ( $search !== NULL ) {
            $value = $search;
            $where = 'searchterms';
        }
    }
}
if ( isset($where) ) {
    include 'inc/Config.php';
    include 'inc/Functions.php';
    $data = Fct::look_for($value, $where);
}

?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Shaarlimages</title>
    <meta name="description" content="Shaarlimages, la galerie des shaarlis !">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="canonical" href="http://shaarlimages.net">
    <link rel="stylesheet" href="assets/css/main.min.css">
    <link type="application/rss+xml" rel="alternate" title="RSS - Shharlimages" href="?do=rss">
    <link rel="icon" type="image/png" href="favicon.png">
    <link rel="apple-touch-icon" type="image/png" href="assets/icon/icon-iphone.png">
    <link rel="apple-touch-icon" sizes="72x72" type="image/png" href="assets/icon/icon-ipad.png">
    <link rel="apple-touch-icon" sizes="114x114" type="image/png" href="assets/icon/icon-iphone4.png">
    <!--[if IE]>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <![endif]-->
</head>
<body>

<!--
    Petit voyeur ;)
    Cette galerie d'image peut-être téléchargée et bidouillée :
        https://github.com/BoboTiG/shaarlimages
-->

<noscript>Oups ! JavaScript doit être activé pour voir la galerie ☹</noscript>
<div id="image-container"></div>

<?php
    if ( isset($data) ) {
        echo '<script>', Fct::generate_json($data, 1), '</script>';
    } else {
        echo '<script src="images.json"></script>';
    }
?>
<script src="assets/js/galinear.min.js"></script>

</body>
</html>
