# centos7 








# centos_ansible.py usage

Utilisation et Log
1. Exécution
Assurez-vous que Python 2.7.5 et le binaire git sont disponibles sur votre système CentOS 7.

## Pour cloner ou mettre a jour la branche 'main' dans /opt/app_config
centos_ansible.py https://github.com/crunchy-devops/essai_ansible_pull.git /opt/app_config -b main

## Journalisation (Logs)
Toutes les actions et erreurs (y compris l'échec de la commande Git) seront enregistrées dans deux endroits :
Console/Terminal : Les messages INFO et ERROR.
Fichier de Log : /var/log/centos_ansible.log pour une trace complète (INFO, DEBUG, ERROR, CRITICAL).