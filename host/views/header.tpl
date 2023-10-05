<!DOCTYPE html>
<html>
<head>
    <link rel="alternate" title="RSS - {{ site["title"] }}" type="application/rss+xml" href="rss">
    <link rel="canonical" href="{{ site["url"] }}">
    <link rel="icon" type="image/png" href="/favicon.png?v={{ version }}">
    <link rel="stylesheet" href="/assets/css/app.css?v={{ version }}" />
    <meta charset="utf-8" />
    <meta name="description" content="{{ site["description"] }}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>{{ site["title"] }}</title>
    %for header in headers:
    {{ !header }}
    %end
</head>

<body>

<!--
    Petit voyeur ;)
    Cette galerie d'image peut-être téléchargée et bidouillée :
        https://github.com/BoboTiG/shaarlimages
-->

<noscript>Oups ! JavaScript doit être activé pour voir la galerie ☹</noscript>
