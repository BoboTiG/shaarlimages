# Shaarlimages

Shaarlimages, la galerie des shaarlis !

URL : [www.shaarlimages.net](https://www.shaarlimages.net)

## Production

Copy all files from the `host` folder to the [PythonAnywhere](https://www.pythonanywhere.com) hosting account.

Details:
- Web app type: Bottle
- Python version: `3.10`
- Force HTTPS: enabled

Tasks:
- "Sync all shaarlis":
  - when: daily at 00:00
  - command: `PYTHONPATH='/home/tiger222/shaarlimages' python -m host sync`

Check [Batteries Included](https://www.pythonanywhere.com/batteries_included/) to know what modules are already provided.

### Backup

Command to fully sync back the data on a local machine:

```console
# Usage:
# rsync -delete -avzhe ssh <USER>@ssh.pythonanywhere.com:<SHAARLIMAGES_FOLDER>/data <LOCAL_FOLDER>/

# Example:
$ rsync -delete -avzhe ssh tiger222@ssh.pythonanywhere.com:/home/tiger222/shaarlimages/data /home/tiger-222/projects/shaarlimages/
```

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

### CLI

```console
$ python -m host -h
```

#### Synchronization

Sync all registered shaarlis:

```console
$ python -m host sync [--force]
```

Sync any shaarlis instance (registered or not):

```console
$ python -m host sync --url URL [--force]

# Example:
# python -m host sync --url 'https://shaarli.example.org/feed/atom'
```

In both cases, use `--force` to (re)sync from the beginning.

---

### Historique

Suite à [cette requête](http://sebsauvage.net/paste/?b1176a415f9bbe17#CIT+sEj+1tsMW8IAWBipoVJiNBcgLt81Gm79rxuiVnU).  

### Ajouter un shaarli

La liste des instances shaarli est récupérée depuis cette [source](host/constants.py#L28) (recherche `FEEDS_URL`).
Si une meilleure source existe, n'hésitez pas à proposer une patch.
Et si votre instance ne figure pas dans cette source, il vous suffira d'être ajouté à celle-ci site pour que vous soyez pris en compte moins de 24h plus tard.

### Remerciements

- Séb pour avoir mis au point [shaarli](http://sebsauvage.net/wiki/doku.php?id=php:shaarli);
- Bronco pour l'inspiration ([feed2array](http://www.warriordudimanche.net/article178/feed2array-obtenir-un-flux-rss-atom-sous-forme-de-tableau)) ;
- Jakob Holmelund pour la [base javascript](https://github.com/jakobholmelund/fitpicsjs) de la partition linéaire ;
- Chromatic.io pour l'[inspiration](http://www.chromatic.io/FQrLQsb) ;
- Arthur Hoaro & Oros42 pour [l'annuaire des shaarlis](https://github.com/Oros42/shaarli-api) ;
- Et tous les contributeurs et testeurs de l'ombre :)
