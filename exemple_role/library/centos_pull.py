#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import subprocess
import os

# ==============================================================================
# DOCUMENTATION du Module centos_pull
# ==============================================================================
DOCUMENTATION = r'''
---
module: centos_pull
short_description: Gère le clone/pull d'un dépôt GitHub et exécute un playbook local sur CentOS.
version_added: "1.0.1"
description:
    - Ce module est conçu pour les hôtes CentOS.
    - Il clone un dépôt si nécessaire.
    - Effectue un 'git pull' si le dépôt existe.
    - Exécute ensuite un playbook Ansible local à l'intérieur du dépôt cloné.
options:
    repo_url:
        description: URL du dépôt Git (ex: https://github.com/user/repo.git).
        required: true
        type: str
    target_dir:
        description: Chemin du répertoire cible où le dépôt doit être cloné/mis à jour (doit être un chemin absolu).
        required: true
        type: str
    playbook_name:
        description: Nom du playbook (ex: site.yml) à exécuter localement après le pull.
        required: true
        type: str
    branch:
        description: Nom de la branche à utiliser.
        required: false
        type: str
        default: main
    tags:
        description: Liste des tags à passer au playbook local (ex: deploy, config).
        required: false
        type: list
        default: []
author:
    - AI Assistant
'''


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main():
    module = AnsibleModule(
        argument_spec=dict(
            repo_url=dict(type='str', required=True),
            target_dir=dict(type='str', required=True),
            playbook_name=dict(type='str', required=True),
            branch=dict(type='str', required=False, default='main'),
            #tags=dict(type='list', required=False, default=[]),
        ),
        supports_check_mode=True
    )

    repo_url = module.params['repo_url']
    target_dir = module.params['target_dir']
    playbook_name = module.params['playbook_name']
    branch = module.params['branch']
    #tags = module.params['tags']

    # État initial
    result = dict(
        changed=False,
        msg='',
        repo_state='unchanged',
        playbook_output=''
    )
    clone_cmd = f"git clone -b {branch} {repo_url} {target_dir}"
    p = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True, check=False)
    # Vérification : Le répertoire .git est-il déjà présent dans la cible ?
    repo_exists = os.path.isdir(target_dir)

    # -------------------------------------------------------------------------
    # 1. Gérer le dépôt (Clone ou Pull)
    # -------------------------------------------------------------------------

    if not repo_exists:
        # Clone
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would clone {repo_url} into {target_dir}")

        # Créer le répertoire si nécessaire
        try:
            os.makedirs(target_dir, exist_ok=True)
        except OSError as e:
            module.fail_json(msg=f"Impossible de créer le répertoire cible {target_dir}: {e}", **result)

        clone_cmd = f"git clone -b {branch} {repo_url} {target_dir}"

        p = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True, check=False)

        if p.returncode != 0:
            module.fail_json(msg=f"Clone failed: {p.stderr}", stdout=p.stdout, **result)

        result['changed'] = True
        result['repo_state'] = 'cloned'
        result['msg'] += f"Dépôt cloné sur {target_dir}. "

    else:
        # Pull (dépôt existe)
        if module.check_mode:
            module.exit_json(changed=True, msg=f"Would pull branch {branch} in {target_dir}")

        # Checkout/Pull
        pull_cmd = f"cd {target_dir} && git fetch && git checkout {branch} && git pull"

        p = subprocess.run(pull_cmd, shell=True, capture_output=True, text=True, check=False, cwd=target_dir)

        if p.returncode != 0:
            module.fail_json(msg=f"Pull failed: {p.stderr}", stdout=p.stdout, **result)

        # Analyse de la sortie pour déterminer si l'état a changé
        if "Already up to date" not in p.stdout and "Already on" not in p.stdout and "up to date" not in p.stdout:
            result['changed'] = True
            result['repo_state'] = 'updated'
            result['msg'] += f"Dépôt mis à jour dans {target_dir}. "
        else:
            result['msg'] += f"Dépôt déjà à jour. "

    # -------------------------------------------------------------------------
    # 2. Exécuter le Playbook local
    # -------------------------------------------------------------------------

    playbook_path = os.path.join(target_dir, playbook_name)
    if not os.path.exists(playbook_path):
        module.fail_json(msg=f"Playbook {playbook_name} non trouvé dans {target_dir}", **result)

    tags_arg = f"--tags {','.join(tags)}" if tags else ""

    # Exécuter le playbook interne avec connexion locale (-c local)
    playbook_cmd = f"ansible-playbook {playbook_name} -c local {tags_arg}"

    p = subprocess.run(playbook_cmd, shell=True, capture_output=True, text=True, check=False, cwd=target_dir)

    if p.returncode != 0:
        # Échec de l'exécution du playbook local
        result['playbook_output'] = p.stdout + p.stderr
        module.fail_json(msg=f"Exécution du playbook {playbook_name} échouée. Code de retour: {p.returncode}", **result)

    # Succès
    result['playbook_output'] = p.stdout
    result['changed'] = True  # On marque toujours comme changé après une exécution de playbook
    result['msg'] += f"Playbook {playbook_name} exécuté avec succès."

    module.exit_json(**result)


if __name__ == '__main__':
    main()