# cpu_stress.py

import multiprocessing
import time
import sys


def cpu_intensive_task(duration):
    """Effectue des calculs intensifs pendant la durée spécifiée."""
    # Obtenir l'heure de début pour la limite de temps
    start_time = time.time()

    # Boucle de calculs (ex: opération sur des nombres)
    while (time.time() - start_time) < duration:
        # Opérations simples pour stresser le CPU
        _ = 1234567 * 7654321 / 1.0
        _ = pow(987654, 0.5)
        _ = [x ** 2 for x in range(1000)]  # Une petite liste compréhension

    print(f"Processus {multiprocessing.current_process().name} terminé.")


def main(duration_sec, num_workers=None):
    """Lance un nombre spécifié de processus pour stresser le CPU."""
    if num_workers is None:
        # Utiliser tous les cœurs disponibles par défaut
        num_workers = multiprocessing.cpu_count()

    print(f"Démarrage du stress test CPU pendant {duration_sec} secondes avec {num_workers} cœurs.")

    # Créer et démarrer les processus
    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(target=cpu_intensive_task, args=(duration_sec,))
        processes.append(p)
        p.start()

    # Attendre que tous les processus soient terminés
    for p in processes:
        p.join()

    print("Stress test CPU terminé.")


if __name__ == '__main__':
    # Durée du stress test en secondes (par défaut : 60 secondes)
    try:
        duration = int(sys.argv[1])
    except (IndexError, ValueError):
        duration = 60

    # Nombre de cœurs à utiliser (par défaut : tous les cœurs)
    try:
        workers = int(sys.argv[2])
    except (IndexError, ValueError):
        workers = None

    main(duration, workers)