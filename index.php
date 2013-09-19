<?php

$do = !empty($_GET['do']) ? $_GET['do'] : NULL;
if ( $do !== NULL ) {
    if ( $do == 'rss' ) {
        include 'config.php';
        include 'inc/Rss.php';
        $nb = !empty($_GET['n']) ? $_GET['n'] : 50;
        $rss = new RSS($nb);
        echo $rss->get_data();
        exit;
    }
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
    <link rel="icon" type="image/png" href="/favicon.png" />
    <link rel="stylesheet" href="/assets/css/main.min.css">
	<link type="application/rss+xml" rel="alternate" title="RSS - Shharlimages" href="/?do=rss" />
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

<div id="image-container"></div>
<noscript>Oups, cette galerie nécessite l'activation de javascript.</noscript>

<script src="/images.json"></script>
<script src="/assets/js/galinear.min.js"></script>

</body>
</html>
