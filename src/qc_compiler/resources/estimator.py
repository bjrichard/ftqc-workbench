from __future__ import annotations

from qc_compiler.circuits import Circuit
from qc_compiler.gates import CNOT, CZ, T
from qc_compiler.resources.estimate import ResourceEstimate


class ResourceEstimator:
    """Estimator for logical circuit resource counts.

    The estimator computes basic logical resource counts from a Circuit.
    It does not model hardware connectivity, routing, measurements,
    feedforward, surface-code costs, or magic-state factories.

    Methods
    -------
    estimate(circuit)
        Return a ResourceEstimate for the input circuit.
    """

    def estimate(self, circuit: Circuit) -> ResourceEstimate:
        """Estimate logical resources for a circuit.

        Parameters
        ----------
        circuit : Circuit
            Circuit to estimate.

        Returns
        -------
        ResourceEstimate
            Logical resource estimate for the circuit.

        Raises
        ------
        TypeError
            If ``circuit`` is not a Circuit object.
        """
        if not isinstance(circuit, Circuit):
            raise TypeError("circuit must be a Circuit object.")

        gate_count = len(circuit)
        t_count = 0
        cnot_count = 0
        cz_count = 0

        for operation in circuit:
            if operation.gate == T:
                t_count += 1

            if operation.gate == CNOT:
                cnot_count += 1

            if operation.gate == CZ:
                cz_count += 1

        return ResourceEstimate(
            gate_count=gate_count,
            t_count=t_count,
            cnot_count=cnot_count,
            cz_count=cz_count,
            ancilla_count=0,
            depth=gate_count,
        )
