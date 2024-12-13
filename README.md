# Quantum-Economic-Behaviour

introduction here

# Previous Methods of Quantum Teleportation

<!-- define teleportation -->
"Teleportation" is the hypothetical transfer of a quantity from one point in space to another without traversing the space in between. 
<!-- outline previous methods of teleportation -->
Methods of teleportation for certain quantities are already well established in the quantum mechanical realm, such as for information and computation. 

## Quantum Information Teleportation

<!-- overview -->
Quantum Information Teleportation (QIT) is a protocol that utilizes Local Operations and Classical Communication (LOCC) to teleport the quantum state of a qubit from one party to another. 
A brief description of the algorithm follows.
<!-- describe QIT algorithm -->
Let there be two parties Alice and Bob (A and B), and let A have a quantum state that she wants to securely communicate to B.
A and B first share two uniformly entangled qubits (an "EPR pair"). This is either given from one to the other, or distributed by a trusted third party. 
A performs an operation between the qubit whose state she wants to share and her EPR qubit, and (as an application of LOCC) measures her qubits and sends said measurements to B.
B then performs one of two operations based on which measurement he recieved, and the result is an exact "copy" of Alice's original state now in Bob's possession.
This doesn't violate the no-cloning theorem because in order for this to happen, the original state first has to be measured, and therefore destroyed.
This essentially means that the state has been "transferred" rather than "copied", and due to the nature of the EPR qubits, this transfer is non-local, making it the "teleportation" of quantum information.

<!-- image of circuit -->
***image of circuit goes here***

<!-- talk about applications -->
QIT is well established in the literature, and has a wide range of applications encompassing communication and computation.
Another form of teleportation can be derived from QIT, namely Quantum Gate Teleportation (QGT).
Utilizing the fact that entire programs can be stored in the state of a single qubit, the resource of quantum computation can also be teleported by simply using QIT on a qubit that represents a program.

In conclusion, both quantum information and quantum computation can be teleported, and the two protocols that do this are essentially equivalent.
But there exists another kind of quantity that can be teleported using a protocol that is in fact "opposite" to QIT, namely "energy". 

# Quantum Energy Teleportation

In 2008, M. Hotta proposed a protocol for Quantum Energy Teleportation (QET).
QET uses a similar circuit to QIT, insofar as it uses LOCC, but parameters are introduced and set in a way that maximizes energy transfer between two locations.





# Quantum Economy
