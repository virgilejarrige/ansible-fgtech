#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Script Python 2.7.5 pour cloner ou mettre a jour un depot Git.
Utilise 'subprocess' pour l'execution de commandes Git.
Inclut une journalisation (logging) complete.
"""

import os
import sys
import argparse
import subprocess
import logging

# Configuration de la journalisation (logging)
LOG_FILE = '/var/log/centos_ansible.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=LOG_FORMAT)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def execute_command(cmd, cwd=None):
    """
    Execute une commande shell et gere les erreurs.
    Retourne (succes, sortie)
    """
    full_cmd = " ".join(cmd)
    logging.info("Execution de la commande: %s (CWD: %s)", full_cmd, cwd or "N/A")

    try:
        # Note: check_output est prefere pour capturer la sortie et gerer les erreurs
        # en Python 2.7.
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, cwd=cwd)
        logging.debug("Commande terminee avec succes. Sortie:\n%s", output)
        return True, output
    except subprocess.CalledProcessError as e:
        logging.error("La commande a echoue avec le code de retour %s. Sortie:\n%s",
                      e.returncode, e.output)
        return False, e.output
    except OSError as e:
        logging.error("Erreur d'execution (Git non trouve?): %s", e)
        return False, str(e)


def git_action(repo_url, branch, target_dir):
    """
    Gere le clonage ou le pull du depot Git.
    """

    git_dir = os.path.join(target_dir, '.git')
    repo_exists = os.path.isdir(git_dir)

    logging.info("Verification du depot a l'emplacement: %s", target_dir)

    if not repo_exists:
        logging.info("Depot non trouve. Tentative de CLONAGE...")

        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
                logging.info("Repertoire cible cree: %s", target_dir)
            except Exception as e:
                logging.error("Impossible de creer le repertoire cible: %s", e)
                sys.exit(1)

        clone_cmd = ['git', 'clone', '--branch', branch, repo_url, target_dir]
        success, output = execute_command(clone_cmd)

        if success:
            logging.info("CLONAGE reussi de %s sur la branche %s.", repo_url, branch)
        else:
            logging.critical("ECHEC du CLONAGE. Sortie Git:\n%s", output)
            sys.exit(1)

    else:
        logging.info("Depot trouve. Tentative de MISE A JOUR (PULL) sur la branche %s...", branch)

        checkout_cmd = ['git', 'checkout', branch]
        success, output = execute_command(checkout_cmd, cwd=target_dir)

        if not success:
            logging.critical("ECHEC du CHECKOUT sur la branche %s. Sortie Git:\n%s", branch, output)
            sys.exit(1)

        pull_cmd = ['git', 'pull', '--ff-only']
        success, output = execute_command(pull_cmd, cwd=target_dir)

        if success:
            if "Already up-to-date" in output or "Already up to date" in output:
                logging.info("PULL reussi: Depot deja a jour.")
            else:
                logging.info("PULL reussi: Depot mis a jour avec succes.")
        else:
            logging.critical("ECHEC du PULL. Sortie Git:\n%s", output)
            sys.exit(1)


def main():
    """
    Fonction principale pour l'analyse des arguments et l'execution.
    """
    parser = argparse.ArgumentParser(
        description='Outil de gestion de depot Git (Clone ou Pull) pour l\'environnement CentOS 7.',
        epilog='Exemple d\'usage: python centos_ansible.py https://github.com/monapp/config.git /opt/app -b develop'
    )

    parser.add_argument(
        'repo_url',
        help='URL complete du depot Git (requis). Exemple: https://github.com/user/repo.git'
    )
    parser.add_argument(
        'target_dir',
        help='Repertoire de travail cible (requis). Le depot y sera clone ou mis a jour.'
    )

    parser.add_argument(
        '-b', '--branch', default='main',
        help='Nom de la branche a utiliser (defaut: main). Le script effectue un checkout avant le pull.'
    )

    args = parser.parse_args()

    try:
        git_action(args.repo_url, args.branch, args.target_dir)
        logging.info("Operation Git terminee avec succes.")
    except Exception as e:
        logging.critical("Une erreur inattendue est survenue: %s", e)
        sys.exit(1)


if __name__ == '__main__':
    main()