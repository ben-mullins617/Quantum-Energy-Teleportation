from protocols.QET_measure_V import AliceProgram, BobProgram
from observe_negative_energy import experiment
from utils import calculate_energy_V

from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

import numpy as np
import itertools
import matplotlib.pyplot as plt


if __name__ == "__main__":
    cfg = StackNetworkConfig.from_file("ideal_network_config.yaml")
    # sweep parameters for h and k
    limits = {
        "h": np.arange(.5, 4, 0.5),
        "k": np.arange(.5, 4, 0.5)
    }
    results = {}
    n_shots = 1000

    for h, k in itertools.product(*limits.values()):
        print(f"{(h,k)=}")

        A, H1, V, E1 = experiment(h, k, n_shots, cfg)

        """
        alice_program = AliceProgram(h, k)
        bob_program = BobProgram(h, k)

        alice_results, bob_results = run(
            config=cfg,
            programs={"Alice": alice_program, "Bob": bob_program},
            num_times=n_shots,
        )

        A, V = calculate_energy_V(alice_results, bob_results, h, k, n_shots)
        """

        exact_A = h ** 2 / np.sqrt(h ** 2 + k ** 2 + 1e-16)

        results[(h, k)] = {
            "A_V":A[0][0],
            "A_V_std":A[0][1],
            "A_H1":A[0][0],
            "A_H1_std":A[0][1],
            "exact_A":exact_A,
            "V":V[0],
            "V_std":V[1],
            "H1":H1[0],
            "H1_std":H1[1],
            "E1":E1[0],
            "E1_std":E1[1]
        }

    print(f"{results}")
    for heatmap_datatype in list(results[list(results.keys())[0]].keys()):
        data = np.array([[results[(h, k)][heatmap_datatype] for h in limits["h"]] for k in limits["k"][::-1]])


        im = plt.imshow(data, cmap='hot_r', interpolation='nearest')
        plt.xticks(range(len(limits["h"])), labels=limits["h"])
        plt.yticks(range(len(limits["k"])), labels=limits["k"][::-1])
        plt.xlabel("h")
        plt.ylabel("k")
        cb = plt.colorbar(im)
        cticks = np.arange(min(data.flatten())), max(data.flatten()), (max(data.flatten())-min(data.flatten()).flatten()/5)
        plt.title(f"<{heatmap_datatype}>")
        plt.savefig(f"images/QET_parameter_sweep_{heatmap_datatype}_{n_shots}.png", bbox_inches="tight")
        cb.remove()
