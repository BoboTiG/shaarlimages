#!/bin/bash
echo "- images  : $(/bin/find data/images -type f | /bin/wc -l)"
echo "- shaarlis: $(/bin/find data/feeds -type f | /bin/wc -l) / $(/bin/grep -c http data/shaarlis.json)"
echo "- storage : $(/bin/du -sh data | /bin/sed 's/data//')"

# Update on 2023-11-03
pythonanywhere=8.48
infomaniak=$(/bin/echo '15.84/12' | /bin/bc)
monthly=$(/bin/echo "${pythonanywhere}+${infomaniak}" | /bin/bc)
echo "- price   : $(/bin/echo "${monthly}*12" | /bin/bc) €/year (or ${monthly} €/month)"
