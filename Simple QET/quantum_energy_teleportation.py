import itertools
import logging
from dataclasses import dataclass
from collections import Counter

from math import acos, sqrt
import numpy
from netqasm.sdk import Qubit
from netqasm.sdk.toolbox.state_prep import set_qubit_state

from squidasm.run.stack.run import run
from squidasm.sim.stack.common import LogManager
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from squidasm.util import create_two_node_network, get_qubit_state, get_reference_state
from squidasm.util.routines import (
    distributed_CNOT_control,
    distributed_CNOT_target,
)



class AliceProgram(Program):
    PEER_NAME = "Bob"

    def __init__(self, h, k):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        # from the minimal hamiltonian model
        self.h = h
        self.k = k
        self.theta = -acos(sqrt(1 - h / sqrt(h ** 2 + k ** 2)) / sqrt(2))

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="alice_program",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=2,
        )

    def run(self, context: ProgramContext):
        connection = context.connection
        csocket = context.csockets[self.PEER_NAME]

        # Prepare the control qubit
        q0 = Qubit(connection)
        q0.rot_Y(angle=2*self.theta)

        # Use the control qubit for a distributed two qubit operation.
        yield from distributed_CNOT_control(
            context, peer_name=self.PEER_NAME, ctrl_qubit=q0
        )

        # inject energy
        q0.H()

        # measure ground state
        m = q0.measure()
        yield from connection.flush()

        # send to Bob
        csocket.send(str(m.value))

        return {
            "measurement": m.value,
        }


class BobProgram(Program):
    PEER_NAME = "Alice"

    def __init__(self, h, k):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        # from the minimal hamiltonian model
        self.h = h
        self.k = k
        self.phi = 0.5*acos((h**2+2*k**2)/sqrt((h**2+2*k**2)**2+h**2*k**2))

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="bob_program",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=2,
        )

    def run(self, context: ProgramContext):
        connection = context.connection
        csocket = context.csockets[self.PEER_NAME]

        # Prepare target qubit
        q1 = Qubit(connection)

        # Use target qubit for a distributed two qubit operation.
        yield from distributed_CNOT_target(
            context, peer_name=self.PEER_NAME, target_qubit=q1
        )

        # receive measurement from Alice
        m = yield from csocket.recv()
        match m:
            case "0":
                # U_1
                q1.rot_Y(angle=2*self.phi)
                ...
            case "1":
                # U_-1
                q1.rot_Y(angle=-2*self.phi)
                ...

        q1.H()

        measurement = q1.measure()

        yield from connection.flush()

        return {
            "measurement": measurement.value,
        }


def calculate_energy(alice_results, bob_results):
    counts = Counter(zip(map(lambda x: x['measurement'], alice_results), map(lambda x: x['measurement'], bob_results)))

    # https://github.com/IKEDAKAZUKI/Quantum-Energy-Teleportation/blob/main/Quantum_Energy_Teleportation.ipynb
    ene_A = (h ** 2) / (sqrt(h ** 2 + k ** 2))
    ene_V = (2 * k ** 2) / (sqrt(h ** 2 + k ** 2))
    error_A = []
    error_V = []
    for orig_bit_string, count in counts.items():
        bit_string = orig_bit_string[::-1]

        ene_A += h * (-1) ** int(bit_string[0]) * count / n_shots
        ene_V += 2 * k * (-1) ** int(bit_string[0]) * (-1) ** int(bit_string[1]) * count / n_shots

        for i in range(count):
            error_A.append(h * (-1) ** int(bit_string[0]))
            error_V.append(2 * k * (-1) ** (int(bit_string[1])))

    return ene_A, ene_V


if __name__ == "__main__":
    cfg = create_two_node_network(node_names=["Alice", "Bob"])

    # initial parameters for ground state, (h,k) = (1.5,1) are found to be optimal for energy transfer
    h = 1.5
    k = 1

    n_shots = 100

    results = {}

    for h,k in itertools.product(numpy.arange(1, 4, 0.5), numpy.arange(1, 4, 0.5)):
        print(f"{(h,k)=}")
        alice_program = AliceProgram(h, k)
        bob_program = BobProgram(h, k)

        alice_results, bob_results = run(
            config=cfg,
            programs={"Alice": alice_program, "Bob": bob_program},
            num_times=n_shots,
        )

        # count outcomes
        counts = Counter(zip(map(lambda x: x['measurement'], alice_results), map(lambda x: x['measurement'], bob_results)))

        print(f"measurement statistics: ", *[str(k[0])+str(k[1])+': '+str(v) for k,v in counts.items()], "", sep="\n")

        A, V = calculate_energy(alice_results, bob_results)

        print("Alice's local energy (measured)", A, )
        print("Alice's local energy (exact)", h ** 2 / sqrt(h ** 2 + k ** 2))
        print("Interacting energy V", V)
        print()

        # since V is negative, B must have lost local energy.
        # since A's measurement does not affect the energy at B, energy must have been teleported from A to B.

        results[(h,k)] = A

    print(results)


