from math import acos, sqrt
from netqasm.sdk.qubit import Qubit

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from squidasm.util.routines import (
    distributed_CNOT_control,
    distributed_CNOT_target,
)


class AliceProgram(Program):
    PEER_NAME = "Bob"

    def __init__(self, h, k):
        self.h = h
        self.k = k
        self.theta = -acos(sqrt(1 - h / sqrt(h ** 2 + k ** 2)) / sqrt(2))

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="alice_program",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=3,
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
        self.h = h
        self.k = k
        self.phi = 0.5*acos((h**2+2*k**2)/sqrt((h**2+2*k**2)**2+h**2*k**2))

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="bob_program",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=3,
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

        # receive measurement from Alice, perform conditional operator U
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

        # receive energy
        #q1.H()
        #q1.X()
        measurement = q1.measure()

        yield from connection.flush()

        return {
            "measurement": measurement.value,
        }
