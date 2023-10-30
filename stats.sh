#!/bin/bash
echo "- images  : $(/bin/find data/images -type f | /bin/wc -l)"
echo "- shaarlis: $(/bin/find data/feeds -type f | /bin/wc -l) / $(/bin/grep -c http data/shaarlis.json)"
echo "- storage : $(/bin/du -sh data | /bin/sed 's/data//')"
echo "- price   : $((10*12)) €/year (or $((10*12/12)) €/month)"