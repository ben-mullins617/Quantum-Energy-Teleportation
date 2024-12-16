from application import AliceProgram, BobProgram
from utils import calculate_energy

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
    n_shots = 100

    for h, k in itertools.product(*limits.values()):
        print(f"{(h,k)=}")
        alice_program = AliceProgram(h, k)
        bob_program = BobProgram(h, k)

        alice_results, bob_results = run(
            config=cfg,
            programs={"Alice": alice_program, "Bob": bob_program},
            num_times=n_shots,
        )

        A, V = calculate_energy(alice_results, bob_results, h, k, n_shots)

        exact_A = h ** 2 / np.sqrt(h ** 2 + k ** 2 + 1e-16)

        results[(h, k)] = {"A":A[0],
                           "A_std":A[1],
                           "exact_A":exact_A,
                           "V":V[0],
                           "V_std":V[1],
                           "A_diff":abs(A[0]-exact_A),
                           "k+h":k+2*h # for testing heatmap orientation/tickers
                           }

    print(results)

    # change to see V or exact_A
    heatmap_datatype = "A_diff"

    data = [[results[(h, k)][heatmap_datatype] for h in limits["h"][::-1]] for k in limits["k"]]


    plt.imshow(data, cmap='hot', interpolation='nearest')
    plt.xticks(range(len(limits["h"])), labels=limits["h"])
    plt.yticks(range(len(limits["k"])), labels=limits["k"][::-1])
    plt.xlabel("h")
    plt.ylabel("k")
    plt.savefig(f"images/QET_parameter_sweep_{heatmap_datatype}_{n_shots}.png", bbox_inches="tight")



