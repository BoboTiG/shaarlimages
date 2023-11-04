# Shaarlimages

Shaarlimages, la galerie des shaarlis !

URL : [www.shaarlimages.net](https://www.shaarlimages.net)

## API

Galleries:
- [/page/NUMBER](https://www.shaarlimages.net/page/42): display the page n° `NUMBER`;
- [/random](https://www.shaarlimages.net/random): display a random image;
- [/search/TERM](https://www.shaarlimages.net/search/animaux), and [/search/TERM/NUMBER](https://www.shaarlimages.net/search/animaux/42): search by term;
- [/tag/TAG](https://www.shaarlimages.net/tag/animaux), and [/tag/TAG/NUMBER](https://www.shaarlimages.net/tag/animaux)/42: search by tag;
- [/zoom/IMAGE](https://www.shaarlimages.net/zoom/urIokw): display the `IMAGE`;

Files:
- [/image/IMAGE](https://www.shaarlimages.net/image/urIokw.jpg): direct link to the original `IMAGE` file;
- [/thumbnail/IMAGE](https://www.shaarlimages.net/thumbnail/urIokw.jpg): direct link to the thumbnail `IMAGE` file;

RSS feeds (a link is made accessible when clicking on "images" at the top-right on the website):
- [/rss](https://www.shaarlimages.net/rss), [/rss/NUMBER](https://www.shaarlimages.net/rss/42), and [/rss/all](https://www.shaarlimages.net/rss/all): global RSS feed (default: last 50 items);
- [/rss/search/TERM](https://www.shaarlimages.net/rss/search/animaux), [/rss/search/TERM/NUMBER](https://www.shaarlimages.net/rss/search/animaux/42), and [/rss/search/TERM/all](https://www.shaarlimages.net/rss/search/animaux/all): RSS feed of the result of the search by term (default: last 50 items);
- [/rss/tag/TAG](https://www.shaarlimages.net/rss/tag/animaux), [/rss/tag/TAG/NUMBER](https://www.shaarlimages.net/rss/tag/animaux/42), and [/rss/tag/TAG/all](https://www.shaarlimages.net/rss/tag/animaux/all): RSS feed of the result of the search by tag (default: last 50 items);

## Production

Copy all files from the `host` folder to the [PythonAnywhere](https://www.pythonanywhere.com) hosting account.

Details:
- Web app type: Bottle
- Python version: `3.10`
- Force HTTPS: enabled

Tasks:
- "Sync all shaarlis":
  - when: daily at 06:00 UTC
  - command: `PYTHONPATH='/home/tiger222/shaarlimages' python -m host sync`

Check [Batteries Included](https://www.pythonanywhere.com/batteries_included/) to know what modules are already provided.

### Backup

Command to fully sync back the data on a local machine:

```console
# Usage:
# rsync -avzhe ssh <USER>@ssh.pythonanywhere.com:<SHAARLIMAGES_FOLDER>/data <LOCAL_FOLDER>/

# Example:
$ rsync -avzhe ssh tiger222@ssh.pythonanywhere.com:/home/tiger222/shaarlimages/data /home/tiger-222/projects/shaarlimages/
```

### OSError: write error

In the server logs, we might see lots of `OSError: write error` messages. They are not related to the current application, [more information here](https://www.pythonanywhere.com/forums/topic/13591/).

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
$ python -m pytest --doctest-modules host tests/unit

# To be run from time to time to ensure solvers are still working
$ python -m pytest tests/integration
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

Sync any Shaarli instance (registered or not):

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

La liste des instances shaarli est récupérée depuis [BoboTiG/shaarlis](https://github.com/BoboTiG/shaarlis). N'hésitez pas à proposer un patch pour ajouter d'autres liens.

### Remerciements

- Séb pour avoir mis au point [shaarli](http://sebsauvage.net/wiki/doku.php?id=php:shaarli);
- Bronco pour l'inspiration ([feed2array](http://www.warriordudimanche.net/article178/feed2array-obtenir-un-flux-rss-atom-sous-forme-de-tableau)) ;
- Jakob Holmelund pour la [base javascript](https://github.com/jakobholmelund/fitpicsjs) de la partition linéaire ;
- Chromatic.io pour l'[inspiration](http://www.chromatic.io/FQrLQsb) ;
- Arthur Hoaro & Oros42 pour [l'annuaire des shaarlis](https://github.com/Oros42/shaarli-api) ;
- Et tous les contributeurs et testeurs de l'ombre :)
