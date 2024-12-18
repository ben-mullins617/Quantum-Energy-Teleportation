from protocols.QET_measure_V import AliceProgram, BobProgram
from observe_negative_energy import experiment
from utils import calculate_energy_V


from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

import numpy as np
import itertools
import matplotlib.pyplot as plt

def sweep(single, double):
    cfg = StackNetworkConfig.from_file("generic_qdevice.yaml")
    cfg.stacks[0].qdevice_cfg["single_qubit_gate_depolar_prob"], cfg.stacks[0].qdevice_cfg["double_qubit_gate_depolar_prob"] = single, double
    print(f"{(single, double)=}")

    A, H1, V, E1 = experiment(h, k, n_shots, cfg)

    exact_A = h**2/np.sqrt(h**2+k**2)

    results[(single, double)] = {
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


if __name__ == "__main__":
    #cfg = StackNetworkConfig.from_file("ideal_network_config.yaml")
    h, k = (1, 1.5)
    n_shots = 100
    limits = {
        "single": np.round(np.arange(0, 1, 0.1), 1),
        "double": np.round(np.arange(0, 1, 0.1), 1)
    }
    results = {}
    for single, double in itertools.product(*limits.values()):
        sweep(single, double)

    print(results)

    for heatmap_datatype in list(results[list(results.keys())[0]].keys()):
        data = np.array([[results[(single, double)][heatmap_datatype] for single in limits["single"]] for double in limits["double"][::-1]])


        im = plt.imshow(data, cmap='hot_r', interpolation='nearest')
        plt.xticks(range(len(limits["single"])), labels=limits["single"])
        plt.yticks(range(len(limits["double"])), labels=limits["double"][::-1])
        plt.xlabel("single gate noise")
        plt.ylabel("double gate noise")
        cb = plt.colorbar(im)
        cticks = np.arange(min(data.flatten())), max(data.flatten()), (max(data.flatten())-min(data.flatten()).flatten()/5)
        plt.title(f"<{heatmap_datatype}>")
        plt.savefig(f"images/QET_noise_sweep_{heatmap_datatype}_{n_shots}.png", bbox_inches="tight")
        cb.remove()