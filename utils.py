import numpy as np
from collections import Counter
import matplotlib.pyplot as plt

def calculate_energy_V(alice_results, bob_results, h, k, n_shots):
    counts = Counter(zip(map(lambda x: x['measurement'], alice_results), map(lambda x: x['measurement'], bob_results)))

    # from https://github.com/IKEDAKAZUKI/Quantum-Energy-Teleportation/blob/main/Quantum_Energy_Teleportation.ipynb
    ene_A = (h ** 2) / (np.sqrt(h ** 2 + k ** 2))
    ene_V = (2 * k ** 2) / (np.sqrt(h ** 2 + k ** 2))
    error_A = []
    error_V = []
    for orig_bit_string, count in counts.items():
        bit_string = orig_bit_string[::-1]

        ene_A += h * (-1) ** int(bit_string[0]) * count / n_shots
        ene_V += 2 * k * (-1) ** int(bit_string[0]) * (-1) ** int(bit_string[1]) * count / n_shots

        for i in range(count):
            error_A.append(h * (-1) ** int(bit_string[0]))
            error_V.append(2 * k * (-1) ** (int(bit_string[1])))

    std_A = np.std(error_A)/np.sqrt(n_shots)
    std_V = np.std(error_V)/np.sqrt(n_shots)
    return (ene_A, std_A), (ene_V, std_V)

def calculate_energy_H1(alice_results, bob_results, h, k, n_shots):
    counts = Counter(zip(map(lambda x: x['measurement'], alice_results), map(lambda x: x['measurement'], bob_results)))

    # from https://github.com/IKEDAKAZUKI/Quantum-Energy-Teleportation/blob/main/Quantum_Energy_Teleportation.ipynb
    ene_A = (h ** 2) / (np.sqrt(h ** 2 + k ** 2))
    ene_B=(h**2)/(np.sqrt(h**2+k**2))
    error_A = []
    error_B = []
    for orig_bit_string, count in counts.items():
        #bit_string = orig_bit_string[::-1]
        bit_string = orig_bit_string

        ene_A += h * (-1) ** int(bit_string[0]) * count / n_shots
        ene_B += h*(-1)**int(bit_string[1])*count/n_shots

        for i in range(count):
            error_A.append(h * (-1) ** int(bit_string[0]))
            error_B.append(h*(-1)**int(bit_string[1]))

    std_A = np.std(error_A) / np.sqrt(n_shots)
    std_B = np.std(error_B)/np.sqrt(n_shots)
    return (ene_A, std_A), (ene_B, std_B)

def plot_histogram(alice_results, bob_results, fig, ax):
    counts = dict(Counter(zip(map(lambda x: x['measurement'], alice_results), map(lambda x: x['measurement'], bob_results))))
    print(counts)
    plt.bar(range(4), [counts[i] for i in sorted(counts)])
    plt.xticks(range(4), ["00", "01", "10", "11"])
    plt.xlabel("Measurements")
    plt.ylabel("Frequency")
    plt.title('Counts')
    #plt.show()
