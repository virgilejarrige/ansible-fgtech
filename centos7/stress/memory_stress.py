# memory_stress.py

import time
import sys
import psutil  # Nécessite l'installation du paquet psutil


def main(target_size_gb):
    """Alloue de la mémoire jusqu'à la taille cible en Go."""
    # Taille d'un élément (nombre entier) en octets (estimation)
    element_size_bytes = 8
    # Taille cible en octets
    target_size_bytes = target_size_gb * (1024 ** 3)

    # Nombre d'éléments nécessaires pour atteindre la taille cible
    num_elements = int(target_size_bytes / element_size_bytes)

    print(f"Démarrage du stress test mémoire. Cible : {target_size_gb} Go.")

    # Liste pour conserver la référence et empêcher le garbage collector de libérer la mémoire
    mega_list = []

    # Remplir la liste par tranches pour surveiller la consommation
    chunk_size = 10 ** 6  # Allouer par blocs d'un million d'éléments

    try:
        for i in range(0, num_elements, chunk_size):
            # Allouer la mémoire : créer une liste de nombres entiers
            chunk = list(range(chunk_size))
            mega_list.extend(chunk)

            # Afficher l'utilisation actuelle de la mémoire
            process = psutil.Process()
            rss_mb = process.memory_info().rss / (1024 ** 2)
            print(
                f"-> Alloué {len(mega_list) * element_size_bytes / (1024 ** 3):.2f} Go. Usage actuel du processus: {rss_mb:.2f} MB")
            time.sleep(0.1)  # Petite pause pour l'affichage

    except MemoryError:
        print("\nERREUR: Allocation mémoire maximale atteinte ou limite système dépassée.")
    except KeyboardInterrupt:
        print("\nArrêté par l'utilisateur.")
    finally:
        # La mémoire sera libérée lorsque le script se terminera
        print(
            f"\nStress test mémoire terminé. Mémoire max allouée : {len(mega_list) * element_size_bytes / (1024 ** 3):.2f} Go.")
        # Garder le programme en vie pour observer l'utilisation de la RAM avant la fin du script
        time.sleep(5)


if __name__ == '__main__':
    # Taille cible de la mémoire à allouer en GB (par défaut: 1 GB)
    try:
        target_gb = float(sys.argv[1])
    except (IndexError, ValueError):
        target_gb = 1.0

    main(target_gb)