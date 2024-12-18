from observe_negative_energy import experiment
from utils import calculate_energy_V

from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

import numpy as np
import itertools
import matplotlib.pyplot as plt


if __name__ == "__main__":
    #cfg = StackNetworkConfig.from_file("ideal_network_config.yaml")
    h, k = (1, 1.5)
    n_shots = 100
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

        A, H1, V, E1 = experiment(h, k, n_shots, cfg)

        exact_A = h ** 2 / np.sqrt(h ** 2 + k ** 2 + 1e-16)

        results[(t1, t2)] = {
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

    print(results)

    for heatmap_datatype in list(results[list(results.keys())[0]].keys()):
        data = np.array([[results[(t1, t2)][heatmap_datatype] if results[(t1, t2)] else 0 for t1 in limits["t1"]] for t2 in limits["t2"][::-1]])


        im = plt.imshow(data, cmap='hot_r', interpolation='nearest')
        plt.xticks(range(len(limits["t1"])), labels=limits["t1"])
        plt.yticks(range(len(limits["t2"])), labels=limits["t2"][::-1])
        plt.xlabel("T1 Coherence (by Order of Magnitude)")
        plt.ylabel("T2 Coherence (by Order of Magnitude)")
        cb = plt.colorbar(im)
        cticks = np.arange(min(data.flatten())), max(data.flatten()), (max(data.flatten()) - min(data.flatten()).flatten() / 5)
        plt.title(f"<{heatmap_datatype}>")
        plt.savefig(f"images/QET_coherence_sweep_{heatmap_datatype}_{n_shots}.png", bbox_inches="tight")
        cb.remove()
