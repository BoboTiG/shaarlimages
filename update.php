<?php

include 'config.php';
$feeds = get_feeds();

?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Shaarlimages - MàJ</title>
    <meta name="description" content="Shaarlimages, la galerie des shaarlis !">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="canonical" href="http://shaarlimages.net/update.php">
    <link rel="icon" type="image/png" href="/favicon.png" />
    <style>
        table {
            
        }
    </style>
</head>
<body>

<?php
    $selected = NULL;
    if ( !empty($_GET['u']) ) {
        $selected = $_GET['u'];
        if ( in_array($_GET['u'], $feeds) ) {
            $ret = read_feed($selected);
            if ( $ret > 0 ) {
                bdd_save();
            }
            echo '<p>'.$selected.' + <b>'.$ret.'</b></p>';
        }
        elseif ( $selected == 'all' ) {
            foreach ( $feeds as $feed ) {
                $ret = read_feed($feed);
                if ( $ret > 0 ) {
                    bdd_save();
                }
                echo '<p>'.$feed.' + <b>'.$ret.'</b></p>';
            }
        }
    }

?>

<table>
    <tr>
        <th>N°</th>
        <th>Link</th>
        <th>Items</th>
        <th>Update</th>
    </tr>
    <tr>
        <td>0</td>
        <td><option>Tous les shaarlis</option></td>
        <td></td>
        <td><a href="?u=all">⥄</a></td>
    </tr>
    <?php
        $i = 0;
        foreach ( $feeds as $feed ) {
            printf(
                '<tr>
                    <td>%d</td>
                    <td>%s</td>
                    <td></td>
                    <td><a href="?u=%s">⥄</a></td>
                </tr>',
                ++$i,
                $feed,
                $feed
            );
        }
        
    ?>
</table>

</body>
</html>
