#! /bin/bash

python impact/manage.py collectstatic --no-input

# En supposant qu'il y avait au moins 8 cores sur la machine et d'après la doc de gunicorn le nombre de workers conseillé était de (2 x $num_cores) + 1
# https://docs.gunicorn.org/en/stable/design.html#how-many-workers
# Ce n'était pas concluant (explosion de la mémoire avec l'option --workers=17)
gunicorn --pythonpath=impact impact.wsgi --log-file -
