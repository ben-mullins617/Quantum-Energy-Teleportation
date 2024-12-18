from protocols.QET_measure_V import AliceProgram as AliceProgram_V, BobProgram as BobProgram_V
from protocols.QET_measure_H1 import AliceProgram as AliceProgram_H1, BobProgram as BobProgram_H1
from utils import calculate_energy_H1, calculate_energy_V

from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

import numpy as np
import itertools
import matplotlib.pyplot as plt


def experiment(h, k, n_shots, cfg):

    # calculate H1
    alice_program_H1 = AliceProgram_H1(h, k)
    bob_program_H1 = BobProgram_H1(h, k)

    alice_results_H1, bob_results_H1 = run(
        config=cfg,
        programs={"Alice": alice_program_H1, "Bob": bob_program_H1},
        num_times=n_shots,
    )

    A_H1, H1 = calculate_energy_H1(alice_results_H1, bob_results_H1, h, k, n_shots)

    # calculate V
    alice_program_V = AliceProgram_V(h, k)
    bob_program_V = BobProgram_V(h, k)

    alice_results_V, bob_results_V = run(
        config=cfg,
        programs={"Alice": alice_program_V, "Bob": bob_program_V},
        num_times=n_shots,
    )

    A_V, V = calculate_energy_V(alice_results_V, bob_results_V, h, k, n_shots)

    return (A_V, A_H1), H1, V, (H1[0]+V[0], H1[1]+V[1])


if __name__ == "__main__":
    h, k = 1.5, 1
    n_shots = 1000

    # 2 node network, no noise
    cfg = StackNetworkConfig.from_file("ideal_network_config.yaml")

    A, H1, V, B = experiment(h, k, n_shots, cfg)

    text = f"""Alice's local energy (measured): {A[0][0]:.5} ± {A[0][1]:.5} (from H1 experiment), {A[1][0]:.5} ± {A[1][1]:.5} (from V experiment)
Alice's local energy (exact): {h**2/np.sqrt(h**2+k**2)}
H1: {H1}
V: {V}
Bob's local energy (H1+V): {H1[0]+V[0]:.5} ± {H1[1]+V[1]:.5}
"""

    print(text)
