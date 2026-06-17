# Week 5 Day 2 notes — Applying operations to statevectors

## Objective

Implement the first exact statevector transformation routine:

```python
def apply_operation_to_statevector(
    operation: Operation,
    statevector: np.ndarray,
) -> np.ndarray:
```

The function applies one local quantum operation to a full `n`-qubit statevector under the project’s little-endian indexing convention.

The central implementation constraint is:

> Apply the local gate matrix directly to the relevant amplitudes without constructing the full `2**n × 2**n` embedded operator.

---

## 1. Abstract states and coordinate vectors

A quantum state is an abstract vector in Hilbert space. A NumPy array is a coordinate representation of that state after choosing a basis.

For an `n`-qubit system, the computational basis is

```text
|0>, |1>, ..., |2**n - 1>
```

or, equivalently,

```text
|00...00>, |00...01>, ..., |11...11>.
```

A general state is

```text
|psi> = sum_x a_x |x>.
```

Its statevector representation is

```text
[a_0, a_1, ..., a_(2**n - 1)].
```

Therefore:

```python
statevector[x]
```

is the amplitude `a_x` of computational basis state `|x>`.

The explicit basis vector corresponding to `|x>` would be column `x` of the identity matrix:

```python
basis = np.eye(2**n, dtype=complex)
ket_x = basis[:, x]
```

However, the simulator does not need to construct this vector. The integer index `x` already identifies the basis vector.

### Example

For four qubits,

```text
|psi> = (|0101> + |1110>) / sqrt(2)
```

is represented as:

```python
statevector = np.zeros(16, dtype=complex)
statevector[5] = 1 / np.sqrt(2)
statevector[14] = 1 / np.sqrt(2)
```

The basis vectors themselves remain implicit.

---

## 2. Little-endian indexing

The project uses little-endian statevector indexing:

```text
index = q0 * 2**0 + q1 * 2**1 + ... + q_(n-1) * 2**(n-1).
```

Qubit `0` is the least significant bit.

For four qubits, a displayed computational basis ket is interpreted as:

```text
|q3 q2 q1 q0>.
```

Example:

```text
|1010>
```

means:

```text
q3 = 1
q2 = 0
q1 = 1
q0 = 0
```

and has index

```text
1 * 2**3 + 0 * 2**2 + 1 * 2**1 + 0 * 2**0 = 10.
```

Thus:

```python
statevector[10]
```

is the amplitude of `|1010>`.

---

## 3. Matrix elements and the notation `<i|U|j>`

For a gate matrix `U`, the matrix element

```text
<i|U|j>
```

means:

1. Start with input basis state `|j>`.
2. Apply `U`.
3. Project the result onto output basis state `|i>`.

In matrix notation:

```text
<i|U|j> = U[i, j].
```

Therefore:

```text
column j = input basis state
row i    = output basis state
```

This follows because multiplying a matrix by a standard basis vector selects one column:

```text
U |j> = column j of U.
```

### Hadamard example

```text
H = (1 / sqrt(2)) [[1,  1],
                   [1, -1]]
```

For input `|0>`, column `0` is used:

```text
H|0> = (|0> + |1>) / sqrt(2).
```

The entries are:

```text
H[0, 0] = 1 / sqrt(2)   contribution to |0>
H[1, 0] = 1 / sqrt(2)   contribution to |1>
```

For input `|1>`, column `1` is used:

```text
H|1> = (|0> - |1>) / sqrt(2).
```

---

## 4. Local operations inside a larger register

Suppose an `n`-qubit state is acted on by a gate supported on `k` selected qubits.

Let:

```text
S     = selected qubits
S_bar = untouched qubits
```

A full basis label can be separated conceptually into:

```text
r = basis configuration on the untouched qubits
s = basis configuration on the selected qubits
```

The full state can be regrouped as:

```text
|psi> = sum_r sum_s a_(r,s) |r>_(S_bar) tensor |s>_S.
```

The number of possible untouched configurations is:

```text
2**(n-k).
```

The number of possible selected configurations is:

```text
2**k.
```

For each fixed untouched configuration `r`, collect the amplitudes over all selected configurations `s`:

```text
v_r = [a_(r,0), a_(r,1), ..., a_(r,2**k - 1)].
```

This vector has length `2**k`, so the local `2**k × 2**k` gate matrix can act on it:

```text
v_r' = U v_r.
```

The gate does not act on `r`. It acts on the amplitude vector indexed by `s`, while `r` is held fixed.

### Important language distinction

`r` is not the vector on which the gate acts.

`r` is a label for one fixed configuration of the untouched qubits.

`v_r` is the local amplitude vector on which the gate acts.

---

## 5. Worked block example

Consider four qubits and a two-qubit gate acting on `q0` and `q3`.

The displayed basis convention is:

```text
|q3 q2 q1 q0>.
```

Selected qubits:

```text
q0, q3
```

Untouched qubits:

```text
q1, q2
```

Fix the untouched configuration:

```text
q2 q1 = 00.
```

The selected bits `q3 q0` vary over:

```text
00, 01, 10, 11.
```

The corresponding full basis states are:

```text
|0000>  index 0
|0001>  index 1
|1000>  index 8
|1001>  index 9
```

The local amplitude block is therefore:

```text
v_00 = [a_0, a_1, a_8, a_9].
```

Apply the local gate:

```text
v_00' = U v_00.
```

Then scatter the four output amplitudes back to indices:

```text
0, 1, 8, 9.
```

Repeat for the other untouched configurations:

```text
q2 q1 = 01 -> [2, 3, 10, 11]
q2 q1 = 10 -> [4, 5, 12, 13]
q2 q1 = 11 -> [6, 7, 14, 15]
```

This is the gather-apply-scatter view of local gate application.

---

## 6. Why the implementation loops over basis indices

For a single computational basis input, only one full basis amplitude may be nonzero.

Example:

```text
|0101>
```

with selected qubits `q0` and `q1` has local input state:

```text
|q1 q0> = |01>.
```

Only that local input basis state is populated.

However, the simulator must support a general statevector:

```text
|psi> = sum_x a_x |x>,
```

where many values of `a_x` may be nonzero.

Therefore the generic implementation loops over every full input basis index:

```python
for input_basis_index in range(statevector.size):
```

For each full basis component, it determines:

- the amplitude at that input index,
- the local input basis state on the selected qubits,
- the relevant column of the gate matrix,
- every possible local output basis state,
- the corresponding full output basis index.

A zero-amplitude input may be skipped:

```python
if input_amplitude == 0:
    continue
```

Even when there is only one populated local input state, multiple local outputs may be produced.

Example:

```text
H|1> = (|0> - |1>) / sqrt(2).
```

One input column can therefore contribute to several output rows.

---

## 7. Extracting one bit from a basis index

To read qubit `q` from a full basis index:

```python
bit = (basis_index >> qubit) & 1
```

This has two stages.

### Stage 1: Right shift

```python
basis_index >> qubit
```

moves the desired bit into position `0`.

Example:

```text
basis_index = 10 = binary 1010
qubit = 1
```

Right shift by one:

```text
1010 >> 1 = 0101.
```

The original bit at position `1` is now at position `0`.

The shift alone does not isolate the bit. Other higher bits remain.

### Stage 2: Bitwise AND mask

```python
... & 1
```

keeps only the least significant bit:

```text
  0101
& 0001
------
  0001
```

So:

```python
(10 >> 1) & 1 == 1
```

### Bitwise AND truth table

```text
1 & 1 = 1
1 & 0 = 0
0 & 1 = 0
0 & 0 = 0
```

`&` is bitwise AND. It is different from Python’s logical `and` operator.

### Important binary values

```text
decimal 1 = binary 0001
decimal 2 = binary 0010
```


## 8. Binary representation and Python shift operators

Python integers are written in decimal by default, but bitwise operators act on their binary representations.

For example:

```python
basis_index = 10
```

means the integer ten. Its binary representation is:

```python
bin(basis_index)  # '0b1010'
```

The prefix `0b` indicates a binary literal or binary-formatted string. The significant bits are `1010`.

For a four-qubit computational basis index:

```text
binary position:  3 2 1 0
qubit:            q3 q2 q1 q0
bits of 10:       1 0 1 0
```

Thus the integer `10` encodes the basis state:

```text
|q3 q2 q1 q0> = |1010>.
```

### Right shift: `>>`

Python syntax:

```python
value >> number_of_positions
```

A right shift moves every bit toward position `0`. Bits that move past position `0` are discarded.

For nonnegative integers, shifting right by `p` positions is equivalent to integer division by `2**p`:

```text
value >> p = floor(value / 2**p).
```

Example:

```python
10 >> 1
```

Binary calculation:

```text
1010 >> 1 = 0101
```

Decimal calculation:

```text
10 // 2 = 5.
```

Therefore:

```python
10 >> 1 == 5
```

A second shift gives:

```text
1010 >> 2 = 0010
```

so:

```python
10 >> 2 == 2
```

In the expression:

```python
(basis_index >> qubit) & 1
```

`>> qubit` does not by itself extract the bit. It moves the bit at position `qubit` into position `0`. The subsequent `& 1` masks away every other bit.

Example for qubit `1` of basis index `10`:

```text
basis index:       1010
right shift by 1:  0101
mask:              0001
                   ----
result:            0001
```

Therefore the bit at position `1` is `1`.

Example for qubit `2`:

```text
basis index:       1010
right shift by 2:  0010
mask:              0001
                   ----
result:            0000
```

Therefore the bit at position `2` is `0`.

### Left shift: `<<`

Python syntax:

```python
value << number_of_positions
```

A left shift moves every bit toward higher positions and appends zeros on the right.

For nonnegative integers, shifting left by `p` positions is equivalent to multiplication by `2**p`:

```text
value << p = value * 2**p.
```

Examples:

```text
1 << 0 = 0001 = 1
1 << 1 = 0010 = 2
1 << 2 = 0100 = 4
1 << 3 = 1000 = 8
```

Therefore:

```python
1 << 3 == 8
```

In `_extract_local_index`, the extracted bit is always `0` or `1`. The expression:

```python
bit << local_position
```

places that bit at the desired position in the local index.

Example:

```python
bit = 1
local_position = 2
```

Then:

```text
0001 << 2 = 0100
```

so the bit contributes `4` to the local index.

If the extracted bit is zero:

```text
0000 << 2 = 0000
```

so it contributes nothing.

### Right shift and left shift are not exact inverses in every context

For a bit that has not been discarded, shifting right and then left may restore its position. However, right shifting can permanently discard low-order bits.

Example:

```text
1011 >> 1 = 0101
0101 << 1 = 1010
```

The original rightmost `1` was discarded, so the final result is not the original integer.

In this simulator:

```text
>> moves a selected bit down to position 0
& 1 isolates that bit
<< moves the isolated bit into a chosen local or full-register position
```

### Related bitwise operators used by the helper functions

```text
&   bitwise AND: keeps a 1 only where both operands have 1
|   bitwise OR:  keeps a 1 where either operand has 1
~   bitwise NOT: flips the bits conceptually
```

Typical simulator uses are:

```python
(index >> qubit) & 1
```

Read one bit.

```python
index | (1 << qubit)
```

Set one bit to `1`.

```python
index & ~(1 << qubit)
```

Set one bit to `0`.

The expression:

```python
1 << qubit
```

creates a mask with a single `1` at the requested qubit position.

Example for `qubit = 3`:

```text
1 << 3 = 1000
```

This single-bit mask is then combined with the index using `|` or `&`.

---

## 9. Packing selected bits into a local index

The helper:

```python
def _extract_local_index(
    basis_index: int,
    qubits: tuple[int, ...],
) -> int:
```

extracts the selected full-register bits and packs them into a local basis index.

The ordering rule is:

```text
qubits[0] -> local bit position 0
qubits[1] -> local bit position 1
...
```

Implementation:

```python
def _extract_local_index(
    basis_index: int,
    qubits: tuple[int, ...],
) -> int:
    """Extract selected qubit bits into a local basis index."""
    local_index = 0

    for local_position, qubit in enumerate(qubits):
        bit = (basis_index >> qubit) & 1
        local_index += bit << local_position

    return local_index
```

The two key lines perform opposite tasks:

```python
bit = (basis_index >> qubit) & 1
```

extracts a bit from its full-register position.

```python
local_index += bit << local_position
```

places that bit into its assigned local position.

---

## 10. Left shift as local-bit placement

A left shift moves a bit to a higher binary position:

```python
bit << local_position
```

For integer bits `0` or `1`, this is equivalent to:

```python
bit * (2**local_position)
```

Examples:

```text
1 << 0 = 0001 = 1
1 << 1 = 0010 = 2
1 << 2 = 0100 = 4
0 << p = 0 for every p
```

### Full packing example

Suppose:

```text
basis_index = 10 = binary 1010
qubits = (1, 2, 3)
```

The selected full-register bits are:

```text
q1 = 1
q2 = 0
q3 = 1
```

The local-position assignment is:

```text
q1 -> local position 0
q2 -> local position 1
q3 -> local position 2
```

Packing:

```text
q1 contribution: 1 << 0 = 001
q2 contribution: 0 << 1 = 000
q3 contribution: 1 << 2 = 100
```

Sum:

```text
001 + 000 + 100 = 101 binary = 5 decimal.
```

Therefore:

```python
_extract_local_index(10, (1, 2, 3)) == 5
```

The selected bit pattern is `101`, and its local basis index is `5`.

### `+=` versus `|=`

This implementation uses:

```python
local_index += bit << local_position
```

because mathematically:

```text
local_index = sum_p bit_p * 2**p.
```

The following is also valid:

```python
local_index |= bit << local_position
```

Bitwise OR more explicitly communicates “set this bit.” Both are correct here because each local bit position starts at zero and is written once.

---

## 11. Why `_extract_local_index` does not need the statevector size

`_extract_local_index` only reads selected bits from an integer basis index.

It receives all information needed for that task:

```text
basis_index -> the full-register bit pattern
qubits      -> which positions to extract
```

It does not need to know how many amplitudes are in the statevector.

Validation that a target qubit lies inside the register belongs in the public function:

```python
num_qubits = _infer_num_qubits(statevector)

if any(qubit >= num_qubits for qubit in operation.qubits):
    raise ValueError(
        "Operation targets a qubit outside the statevector."
    )
```

This separation keeps the helper focused:

```text
apply_operation_to_statevector:
    validates operation qubits against the register size

_extract_local_index:
    assumes valid inputs and performs bit extraction only
```

---

## 12. Inferring the number of qubits

A valid `n`-qubit statevector has length:

```text
2**n.
```

Therefore:

```text
n = log2(statevector length).
```

A clear implementation is:

```python
import math


def _infer_num_qubits(statevector: np.ndarray) -> int:
    """Infer the number of qubits represented by a statevector."""
    if statevector.ndim != 1:
        raise ValueError("Statevector must be one-dimensional.")

    size = statevector.size

    if size == 0:
        raise ValueError("Statevector must be nonempty.")

    num_qubits = math.log2(size)

    if not num_qubits.is_integer():
        raise ValueError(
            "Statevector length must be a power of two."
        )

    return int(num_qubits)
```

This directly expresses the mathematical invariant and is fully professional.

A bitwise power-of-two test is possible, but it is not required:

```python
(size & (size - 1)) == 0
```

The logarithmic version is preferred here because it is clearer for this codebase and audience.

---

## 13. Replacing selected bits in a full basis index

The inverse operation of `_extract_local_index` is to take a local output index and place its bits back into the selected full-register positions.

Suggested helper:

```python
def _replace_local_bits(
    basis_index: int,
    qubits: tuple[int, ...],
    local_index: int,
) -> int:
```

Conceptually:

1. Start from `basis_index`.
2. Read each bit of `local_index`.
3. Write that bit into the corresponding full-register qubit position.
4. Leave all untouched qubit bits unchanged.

A separate `_set_bit` helper may be used:

```python
def _set_bit(
    index: int,
    qubit: int,
    bit: int,
) -> int:
```

One readable implementation strategy is:

```python
def _set_bit(index: int, qubit: int, bit: int) -> int:
    """Return an index with one bit replaced."""
    if bit == 0:
        return index & ~(1 << qubit)

    return index | (1 << qubit)
```

Then:

```python
def _replace_local_bits(
    basis_index: int,
    qubits: tuple[int, ...],
    local_index: int,
) -> int:
    """Replace selected full-register bits using a local index."""
    output_basis_index = basis_index

    for local_position, qubit in enumerate(qubits):
        bit = (local_index >> local_position) & 1
        output_basis_index = _set_bit(
            output_basis_index,
            qubit,
            bit,
        )

    return output_basis_index
```

---

## 14. Applying one operation to the full statevector

The public function structure is:

```python
def apply_operation_to_statevector(
    operation: Operation,
    statevector: np.ndarray,
) -> np.ndarray:
    """Apply one quantum operation to a full statevector."""
    if not isinstance(operation, Operation):
        raise TypeError("operation must be an Operation.")

    if not isinstance(statevector, np.ndarray):
        raise TypeError("statevector must be a NumPy array.")

    num_qubits = _infer_num_qubits(statevector)

    if any(qubit >= num_qubits for qubit in operation.qubits):
        raise ValueError(
            "Operation targets a qubit outside the statevector."
        )

    gate_matrix = get_gate_matrix(operation.gate)
    result = np.zeros(statevector.shape, dtype=complex)

    for input_basis_index in range(statevector.size):
        input_amplitude = statevector[input_basis_index]

        if input_amplitude == 0:
            continue

        local_input_index = _extract_local_index(
            input_basis_index,
            operation.qubits,
        )

        for local_output_index in range(gate_matrix.shape[0]):
            coefficient = gate_matrix[
                local_output_index,
                local_input_index,
            ]

            if coefficient == 0:
                continue

            output_basis_index = _replace_local_bits(
                input_basis_index,
                operation.qubits,
                local_output_index,
            )

            result[output_basis_index] += (
                coefficient * input_amplitude
            )

    return result
```

---

## 15. Meaning of the two loops

### Full input basis loop

```python
for input_basis_index in range(statevector.size):
```

This loops over every computational basis component of the full input state.

For each index, the simulator reads:

```python
input_amplitude = statevector[input_basis_index]
```

### Local output basis loop

```python
for local_output_index in range(gate_matrix.shape[0]):
```

`gate_matrix.shape[0]` is the number of rows in the gate matrix.

For a `k`-qubit gate:

```text
gate_matrix.shape == (2**k, 2**k).
```

The local input index fixes one column. Looping over rows considers every possible local output basis state.

The matrix lookup:

```python
coefficient = gate_matrix[
    local_output_index,
    local_input_index,
]
```

is the matrix element:

```text
<local_output| U |local_input>.
```

Interpretation:

```text
column = current local input basis state
row    = one possible local output basis state
```

---

## 16. Central amplitude update

The core transformation is:

```python
result[output_basis_index] += (
    gate_matrix[local_output_index, local_input_index]
    * statevector[input_basis_index]
)
```

Mathematically:

```text
new amplitude at output index
    +=
local transition amplitude
    ×
old amplitude at input index.
```

Equivalently:

```text
b_y += U[i, j] a_x,
```

where:

```text
x = full input basis index
y = full output basis index
j = local input basis index extracted from x
i = local output basis index inserted into y
```

The untouched bits in `x` and `y` are identical. Only the selected qubit bits may differ.

The `+=` is essential because several different input basis components can contribute to the same output basis component under a general linear transformation.

---

## 17. One-qubit Hadamard example inside a larger register

Start from:

```text
|0101>
```

and apply `H` to `q0`.

Since `q0 = 1`, the local input index is:

```text
1.
```

Therefore column `1` of `H` is used:

```text
[1/sqrt(2), -1/sqrt(2)].
```

Possible local outputs:

```text
local output 0 -> q0 becomes 0
local output 1 -> q0 becomes 1
```

The untouched bits `q3 q2 q1 = 010` remain fixed.

Thus:

```text
H_q0 |0101>
    = (|0100> - |0101>) / sqrt(2).
```

This example shows why one populated input basis component may produce several output basis components.

---

## 18. Non-adjacent controlled-NOT example

Apply controlled-NOT (CNOT) to qubits:

```python
operation.qubits = (0, 3)
```

under the project convention:

```text
qubits[0] = control
qubits[1] = target
```

For full input:

```text
|0001>
```

we have:

```text
q0 = 1
q3 = 0.
```

The local basis ordering follows `operation.qubits`:

```text
q0 -> local position 0
q3 -> local position 1
```

So the local input bits are:

```text
q3 q0 = 01
```

with local input index `1`.

The CNOT matrix column for local input `|01>` maps to local output `|11>`.

Therefore:

```text
q0 remains 1
q3 changes from 0 to 1
```

and:

```text
|0001> -> |1001>.
```

The full indices are:

```text
1 -> 9.
```

The untouched qubits `q1` and `q2` remain unchanged.

---

## 19. Functions to implement

The Week 5 Day 2 implementation currently consists of:

```python
def apply_operation_to_statevector(
    operation: Operation,
    statevector: np.ndarray,
) -> np.ndarray:
    ...
```

```python
def _infer_num_qubits(statevector: np.ndarray) -> int:
    ...
```

```python
def _extract_local_index(
    basis_index: int,
    qubits: tuple[int, ...],
) -> int:
    ...
```

```python
def _replace_local_bits(
    basis_index: int,
    qubits: tuple[int, ...],
    local_index: int,
) -> int:
    ...
```

Optionally:

```python
def _set_bit(index: int, qubit: int, bit: int) -> int:
    ...
```

A standalone `_get_bit` helper is optional because the extraction expression is already short:

```python
(index >> qubit) & 1
```

---

## 20. Validation responsibilities

### `_infer_num_qubits`

Should validate:

- statevector is one-dimensional,
- statevector is nonempty,
- statevector length is a power of two.

### `apply_operation_to_statevector`

Should validate:

- `operation` is an `Operation`,
- `statevector` is a NumPy array,
- all target qubit indices are smaller than the inferred register size,
- the operation’s gate matrix is supported through `get_gate_matrix`.

### Private bit helpers

May assume that:

- indices are nonnegative,
- qubit positions are valid,
- local indices are within the expected gate dimension.

These assumptions are acceptable because the public function performs boundary validation.

---

## 21. Tests to add

At minimum, tests should cover:

### One-qubit operations

- `X|0> = |1>`
- `X|1> = |0>`
- `H|0> = (|0> + |1>) / sqrt(2)`
- `H|1> = (|0> - |1>) / sqrt(2)`

### Operations on different full-register qubits

- `X` on `q0` flips the least significant bit.
- `X` on `q1` flips the next bit.

### Two-qubit operations

- CNOT on `(0, 1)` follows the documented little-endian convention.
- CNOT on non-adjacent qubits such as `(0, 3)` preserves untouched bits.
- CZ applies a phase only when both selected bits are `1`.

### Superpositions

- linear combinations transform correctly,
- multiple input amplitudes accumulate correctly,
- Hadamard creates the expected superposition.

### API behavior

- input statevector is not mutated,
- returned array has complex dtype,
- invalid dimensionality is rejected,
- empty arrays are rejected,
- non-power-of-two lengths are rejected,
- out-of-range qubit targets are rejected,
- non-`Operation` inputs are rejected,
- non-NumPy statevectors are rejected.

### Helper behavior

- `_extract_local_index` preserves the ordering of `qubits`,
- `_replace_local_bits` changes only selected positions,
- extraction and replacement agree on local bit ordering.

---

## 22. Core mental model

The entire algorithm can be summarized as:

```text
The full basis index identifies one full-register input basis state.

The selected qubit positions determine a local input basis index.

That local input index selects one column of the gate matrix.

Each row of that column gives the amplitude contribution to one local output basis state.

The local output bits are inserted back into the selected full-register positions.

The untouched bits remain unchanged.

The resulting contribution is accumulated in the output statevector.
```

Or in one formula:

```text
result[y] += U[i, j] * statevector[x].
```

---

## 23. What is deliberately not being constructed

The implementation does not need to construct:

- explicit computational basis vectors,
- columns of a `2**n × 2**n` identity matrix,
- a symbolic linear combination of basis vectors,
- the full embedded operator `I tensor U tensor I`,
- reduced density matrices,
- separate physical states for individual qubits.

The simulator needs only:

- the statevector amplitudes,
- integer basis indices,
- selected qubit positions,
- the local gate matrix,
- bit extraction and replacement.

---

## 24. Precision of language

Avoid saying:

```text
The gate changes the amplitude of a qubit.
```

In a general entangled state, individual qubits do not possess independent amplitudes.

Prefer:

```text
The gate changes the amplitudes of full-register computational basis states by acting on the selected local basis index while the untouched bits remain fixed.
```

Similarly, do not describe the procedure as physically reducing the state to a smaller state. The local vectors `v_r` are amplitude blocks or slices of the full statevector, not independent subsystem states in general.

---

## 25. Day 2 implementation checkpoint

Before moving to full-circuit simulation, the following should be true:

- the helper functions are implemented,
- the local qubit ordering is explicit and tested,
- one operation can be applied without constructing a full operator,
- input arrays are not mutated,
- one-qubit and two-qubit examples pass,
- little-endian CNOT behavior is verified,
- non-adjacent target qubits are verified,
- all tests pass.

Expected commit:

```bash
feat(simulation): apply operations to statevectors
```

## References

1. Michael J. McGuffin, Jean-Marc Robert, and Kazuki Ikeda, “How to Write a Simulator for Quantum Circuits from Scratch: A Tutorial,” arXiv:2506.08142, 2025.  
   Directly relevant to statevector representation, basis indexing, and applying local gates without constructing the full-system operator.

2. Tyson Jones, Anna Brown, Ian Bush, and Simon Benjamin, “QuEST and High Performance Simulation of Quantum Computers,” arXiv:1802.08032, 2018.  
   Provides broader context on statevector and density-matrix simulation, controlled operations, parallelization, and high-performance simulator design.

3. Mikhail Smelyanskiy, Nicolas P. D. Sawaya, and Alán Aspuru-Guzik, “qHiPSTER: The Quantum High Performance Software Testing Environment,” arXiv:1601.07195, 2016.  
   Useful for understanding efficient statevector updates, bit-based indexing, vectorization, threading, and cache-aware simulation.

4. Gian Giacomo Guerreschi, Justin Hogaboam, Fabio Baruffa, and Nicolas P. D. Sawaya, “Intel Quantum Simulator: A Cloud-Ready High-Performance Simulator of Quantum Circuits,” arXiv:2001.10554, 2020.  
   Extends the qHiPSTER approach and discusses distributed statevector simulation and implementation architecture.

5. IBM Quantum Documentation, “Bit ordering in the Qiskit SDK.”  
   Documents the convention that qubit 0 is the least significant bit, qubit \(q\) contributes \(2^q\) to a computational-basis index, and bitstrings are displayed with the most significant bit on the left.

6. Google Quantum AI, “qsim and qsimh.”  
   Describes full-statevector Schrödinger simulation and hybrid Schrödinger–Feynman simulation in Google’s qsim simulator.

7. Sergei V. Isakov et al., “Simulations of Quantum Circuits with Approximate Noise using qsim and Cirq,” arXiv:2111.02396, 2021.  
   Relevant for later work involving noisy simulation, quantum trajectories, and simulator performance.
