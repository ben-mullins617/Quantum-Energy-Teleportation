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
    n_shots = 10
    limits = {
        "t1": range(0, 11),
        "t2": range(0, 11)
    }
    results = {}
    for t1, t2 in itertools.product(*limits.values()):
        if t2 > t1: # not allowed by netsquid
            results[(t1, t2)] = {}
            continue
        cfg = StackNetworkConfig.from_file("generic_qdevice.yaml")
        cfg.stacks[0].qdevice_cfg["T1"], cfg.stacks[0].qdevice_cfg["T2"] = 10**t1, 10**t2
        print(f"{(t1, t2)=}")

        alice_program = AliceProgram(h, k)
        bob_program = BobProgram(h, k)

        alice_results, bob_results = run(
            config=cfg,
            programs={"Alice": alice_program, "Bob": bob_program},
            num_times=n_shots,
        )

        A, V = calculate_energy(alice_results, bob_results, h, k, n_shots)

        exact_A = h ** 2 / np.sqrt(h ** 2 + k ** 2 + 1e-16)

        results[(t1, t2)] = {"A":A[0],
                           "A_std":A[1],
                           "exact_A":exact_A,
                           "V":V[0],
                           "V_std":V[1],
                           "A_diff":abs(A[0]-exact_A),
                           }

    print(results)

    for heatmap_datatype in list(results[list(results.keys())[0]].keys()):
        data = np.array([[results[(t1, t2)][heatmap_datatype] if results[(t1, t2)] else 0 for t1 in limits["t1"]] for t2 in limits["t2"][::-1]])


        im = plt.imshow(data, cmap='hot_r', interpolation='nearest')
        plt.xticks(range(len(limits["t1"])), labels=limits["t1"])
        plt.yticks(range(len(limits["t2"])), labels=limits["t2"][::-1])
        plt.xlabel("t1")
        plt.ylabel("t2")
        cb = plt.colorbar(im)
        cticks = np.arange(min(data.flatten())), max(data.flatten()), (max(data.flatten()) - min(data.flatten()).flatten() / 5)
        plt.savefig(f"images/QET_coherence_sweep_{heatmap_datatype}_{n_shots}.png", bbox_inches="tight")
        cb.remove()
