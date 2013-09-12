ShaarlImages
===

Shaarlimages, la galerie des shaarlis !

Démo : [shaarlimages.net](http://shaarlimages.net)

Informations
---

Suite à [cette requête](http://sebsauvage.net/paste/?b1176a415f9bbe17#CIT+sEj+1tsMW8IAWBipoVJiNBcgLt81Gm79rxuiVnU).  
Cette galerie s'inspire honteusement de [celle-ci](http://www.chromatic.io/FQrLQsb), et repose 
sur le principe de [partition linéaire](http://www.crispymtn.com/stories/the-algorithm-for-a-perfectly-balanced-photo-gallery).  
Le code javascript a été largement inspiré par celui de [jakobholmelund / fitpicsjs](https://github.com/jakobholmelund/fitpicsjs), 
amélioré et porté en javascript natif (plus besoin de grosses bibliothèques telles que jQuery, Prototype, ...).

Améliorations possibles
---

Dans l'immédiat, la couleur de fond pour chaque image est calculée (couleur moyenne dominante) et une image est ajoutée par dessus pour le grain. Bien que ça rende pas trop mal, il faudrait revoir le mécanisme pour se rapprocher un peu plus de [cette galerie]([celle-ci](http://www.chromatic.io/FQrLQsb).  
Pour le reste, libre à vous de forker, bidouiller et proposer des patches ;)

Pré-requis
---

Pour auto-héberger une galerie, en l'état, il vous faudra PHP 5. C'est tout.
