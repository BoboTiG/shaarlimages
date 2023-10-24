<!DOCTYPE html>
<html>
<head>
    <link rel="canonical" href="{{ site.url }}">
    <link rel="icon" type="image/png" href="/favicon.png?v={{ version }}">
    <link rel="stylesheet" href="/assets/css/app.css?v={{ version }}" />
    <meta charset="utf-8" />
    <meta name="description" content="{{ site.description }}">
    <meta property="og:description" content="{{ site.description }}" />
    <meta property="og:title" content="{{ site.title }}" />
    <meta property="og:url" content="{{ site.url }}" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>{{ site.title }}</title>
    %for header in headers:
    {{ !header }}
    %end
</head>

<body>

<!--
    Ouh ! Un hackeur est parmi nous ? Ou peut-être une hackeuse ?
    Bref, cette galerie d’images fort sympathique peut-être téléchargée et bidouillée :
        https://github.com/BoboTiG/shaarlimages
-->

<noscript>Oups ! JavaScript doit être activé pour voir la galerie ☹</noscript>
