from protocols.QET_measure_V import AliceProgram, BobProgram
from utils import calculate_energy_V, plot_histogram

from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

import numpy as np
from collections import Counter
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # initial parameters for ground state
    # (h,k) = (1.5,1) are found to be sufficiently optimal for energy transfer
    h = 1.5
    k = 1
    n_shots = 1000

    alice_program = AliceProgram(h, k)
    bob_program = BobProgram(h, k)

    # 2 node network, no noise
    cfg = StackNetworkConfig.from_file("ideal_network_config.yaml")

    alice_results, bob_results = run(
        config=cfg,
        programs={"Alice": alice_program, "Bob": bob_program},
        num_times=n_shots,
    )

    # count outcomes
    counts = Counter(zip(
        map(lambda x: x['measurement'], alice_results),
        map(lambda x: x['measurement'], bob_results)
    ))

    print(f"measurement statistics: ", *[str(k[0]) + str(k[1]) + ': ' + str(v) for k, v in counts.items()], "",
          sep="\n")

    A, V = calculate_energy_V(alice_results, bob_results, h, k, n_shots)

    exact_A = h ** 2 / np.sqrt(h ** 2 + k ** 2)

    text = f"""Alice's local energy (measured): {A[0]:.5} ± {A[1]:.5}
Alice's local energy (exact): {exact_A:.5}
Interacting energy V: {V[0]:.5} ± {V[1]:.5}"""

    print(text)

    # If V is negative, B must have lost local energy.
    # A's measurement does not affect the energy at B, so energy must have been teleported from A to B.

    fig, ax = plt.subplots()
    plot_histogram(alice_results, bob_results, fig, ax)

    fig.text(0.05, 0, text, va='top')
    #fig.tight_layout()
    plt.savefig(f"images/QET_simulation_counts_{n_shots}.png", bbox_inches="tight")
