# Shaarlimages

Shaarlimages, la galerie des shaarlis !

URL : [shaarlimages.net](https://shaarlimages.net)

## Production

Copy all files from the `host` folder to the [PythonAnywhere](https://www.pythonanywhere.com) hosting account.

Details:
- Web app type: Bottle
- Python version: `3.10`
- Force HTTPS: enabled

Check [Batteries Included](https://www.pythonanywhere.com/batteries_included/) to know what modules are already provided.

## Development

### Installation

```console
$ python3.10 -m venv venv
$ . venv/bin/activate
$ python -m pip install -U pip
$ python -m pip install -r requirements-dev.txt
```

### Quality

```console
$ ./checks.sh
```

### Tests

```console
$ python -m pytest --doctest-modules host tests
```

### Local Server

```console
$ python server.py
```

--

### Informations

Suite à [cette requête](http://sebsauvage.net/paste/?b1176a415f9bbe17#CIT+sEj+1tsMW8IAWBipoVJiNBcgLt81Gm79rxuiVnU).  
Cette galerie s'inspire honteusement de [celle-ci](http://www.chromatic.io/FQrLQsb), et repose 
sur le principe de [partition linéaire](http://www.crispymtn.com/stories/the-algorithm-for-a-perfectly-balanced-photo-gallery) (pas de perte d'espace).  
Le code javascript a été largement inspiré par celui de [jakobholmelund / fitpicsjs](https://github.com/jakobholmelund/fitpicsjs), 
amélioré et porté en javascript natif (plus besoin de grosses bibliothèques telles que jQuery, Prototype, ...).

### Ajouter un shaarli

J'utilise la liste d'export de [shaarli.fr](http://shaarli.fr/opml?mod=opml), donc il vous suffira d'être ajouté sur ce site pour que vous soyez pris en compte.  


### Améliorations possibles

Dans l'immédiat, la couleur de fond pour chaque image est calculée (couleur moyenne dominante) et une image est ajoutée par dessus pour le grain. Bien que ça rende pas trop mal, il faudrait revoir le mécanisme pour se rapprocher un peu plus de [cette galerie](http://www.chromatic.io/FQrLQsb).  
Pour le reste, libre à vous de forker, bidouiller et proposer des patches ;)

### Détails techniques

Reportez-vous au dépôt [Galinear](https://github.com/BoboTiG/galinear) pour plus d'informations. Il s'agit du système de la galerie seul, plus facile pour bidouiller.

### Remerciements

- Séb pour avoir mis au point [shaarli ;](http://sebsauvage.net/wiki/doku.php?id=php:shaarli)  
- Bronco pour l'inspiration ([feed2array](http://www.warriordudimanche.net/article178/feed2array-obtenir-un-flux-rss-atom-sous-forme-de-tableau)) ;  
- Jakob Holmelund pour la [base javascript](https://github.com/jakobholmelund/fitpicsjs) de la partition linéaire ;  
- Chromatic.io pour l'[inspiration](http://www.chromatic.io/FQrLQsb) ;  
- Et tous les contributeurs et testeurs de l'ombre :)
