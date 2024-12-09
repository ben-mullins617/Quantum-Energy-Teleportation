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

    def __init__(self, K, J):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        # from the minimal hamiltonian model
        self.K = K
        self.J = J

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

