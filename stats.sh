#!/bin/bash
echo "- images  : $(/bin/find data/images -type f | /bin/wc -l)"
echo "- shaarlis: $(/bin/find data/feeds -type f | /bin/wc -l) / $(/bin/grep -c http data/shaarlis.json)"
echo "- storage : $(/bin/du -sh data | /bin/sed 's/data//')"

# Updated on 2023-11-03
pythonanywhere=8.95
infomaniak=$(python3 -c 'print(15.84 / 12)')
monthly=$(python3 -c "print(${pythonanywhere} + ${infomaniak})")
echo "- price   : $(python3 -c "print(${monthly} * 12)") €/year (or ${monthly} €/month)"
