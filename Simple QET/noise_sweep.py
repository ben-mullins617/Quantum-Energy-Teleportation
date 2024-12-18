from application import AliceProgram, BobProgram
from utils import calculate_energy

from squidasm.run.stack.config import StackNetworkConfig, GenericQDeviceConfig, StackConfig
from squidasm.run.stack.run import run

import numpy as np
import itertools
import matplotlib.pyplot as plt


if __name__ == "__main__":
    #cfg = StackNetworkConfig.from_file("ideal_network_config.yaml")
    h, k = (1, 1.5)
    n_shots = 1000
    limits = {
        "single": np.round(np.arange(0, 1, 0.1), 1),
        "double": np.round(np.arange(0, 1, 0.1), 1)
    }
    results = {}
    for single, double in itertools.product(*limits.values()):
        cfg = StackNetworkConfig.from_file("generic_qdevice.yaml")
        cfg.stacks[0].qdevice_cfg["single_qubit_gate_depolar_prob"], cfg.stacks[0].qdevice_cfg["single_qubit_gate_depolar_prob"] = single, double
        print(f"{(single, double)=}")

        alice_program = AliceProgram(h, k)
        bob_program = BobProgram(h, k)

        alice_results, bob_results = run(
            config=cfg,
            programs={"Alice": alice_program, "Bob": bob_program},
            num_times=n_shots,
        )

        A, V = calculate_energy(alice_results, bob_results, h, k, n_shots)

        exact_A = h ** 2 / np.sqrt(h ** 2 + k ** 2 + 1e-16)

        results[(single, double)] = {"A":A[0],
                           "A_std":A[1],
                           "exact_A":exact_A,
                           "V":V[0],
                           "V_std":V[1],
                           "A_diff":abs(A[0]-exact_A),
                           }

    print(results)

    for heatmap_datatype in list(results[list(results.keys())[0]].keys()):
        data = np.array([[results[(single, double)][heatmap_datatype] for single in limits["single"]] for double in limits["double"][::-1]])


        im = plt.imshow(data, cmap='hot_r', interpolation='nearest')
        plt.xticks(range(len(limits["single"])), labels=limits["single"])
        plt.yticks(range(len(limits["double"])), labels=limits["double"][::-1])
        plt.xlabel("single")
        plt.ylabel("double")
        cb = plt.colorbar(im)
        cticks = np.arange(min(data.flatten())), max(data.flatten()), (max(data.flatten())-min(data.flatten()).flatten()/5)
        plt.savefig(f"images/QET_noise_sweep_{heatmap_datatype}_{n_shots}.png", bbox_inches="tight")
        cb.remove()