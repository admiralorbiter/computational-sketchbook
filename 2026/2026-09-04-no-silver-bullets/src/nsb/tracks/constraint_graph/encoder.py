"""Schoolbook binary multiplication CNF encoder for integer factorization."""

from typing import Dict, List, Optional, Tuple
from pysat.formula import CNF


class VarManager:
    """Manages 1-based variable indices for CNF encoding."""

    def __init__(self, start: int = 1):
        self._next_var = start

    def new_var(self) -> int:
        var = self._next_var
        self._next_var += 1
        return var

    def new_vars(self, count: int) -> List[int]:
        return [self.new_var() for _ in range(count)]

    @property
    def total_vars(self) -> int:
        return self._next_var - 1


class SchoolbookSATEncoder:
    """Encodes p * q = N as a CNF formula using schoolbook binary multiplication with full adders."""

    def __init__(self, symmetry_breaking: bool = True, inject_malformed_carry: bool = False):
        self.symmetry_breaking = symmetry_breaking
        self.inject_malformed_carry = inject_malformed_carry

    def encode(self, N: int, bp: Optional[int] = None, bq: Optional[int] = None) -> Tuple[CNF, Dict[str, List[int]]]:
        """Encode p * q = N into CNF.

        Args:
            N: Target integer modulus (must be odd).
            bp: Bit length of factor p (defaults to bit_length(N)//2).
            bq: Bit length of factor q (defaults to bit_length(N) - bp).

        Returns:
            Tuple[CNF, mapping_dict] where mapping_dict contains variable indices for p and q bits.
        """
        if N % 2 == 0:
            raise ValueError("Modulus N must be odd for semiprime factorization")

        nbits = N.bit_length()
        bp = bp or (nbits // 2)
        bq = bq or (nbits - bp)

        vm = VarManager()
        cnf = CNF()

        # Variable allocation for factors
        # p = sum_{i=0}^{bp-1} p_i * 2^i
        # q = sum_{j=0}^{bq-1} q_j * 2^j
        p_vars = vm.new_vars(bp)
        q_vars = vm.new_vars(bq)

        # Boundary constraints: factors are odd, so p_0 = 1, q_0 = 1
        cnf.append([p_vars[0]])
        cnf.append([q_vars[0]])

        # MSB constraints: p_{bp-1} = 1, q_{bq-1} = 1
        cnf.append([p_vars[bp - 1]])
        cnf.append([q_vars[bq - 1]])

        # Symmetry breaking: p <= q if bp == bq
        if self.symmetry_breaking and bp == bq:
            self._add_less_than_or_equal(cnf, vm, p_vars, q_vars)

        # Partial products: a_{i,j} = p_i AND q_j
        # Clause representation for a <-> (p AND q):
        # (~p | ~q | a), (p | ~a), (q | ~a)
        pp: Dict[Tuple[int, int], int] = {}
        for i in range(bp):
            for j in range(bq):
                if i == 0 and j == 0:
                    a = vm.new_var()
                    cnf.append([a])
                    pp[(i, j)] = a
                else:
                    a = vm.new_var()
                    pi = p_vars[i]
                    qj = q_vars[j]
                    cnf.append([-pi, -qj, a])
                    cnf.append([pi, -a])
                    cnf.append([qj, -a])
                    pp[(i, j)] = a

        # Grid of columns to sum
        # Column k has bits where i + j = k
        columns: List[List[int]] = [[] for _ in range(bp + bq)]
        for (i, j), var in pp.items():
            columns[i + j].append(var)

        incoming_carries: List[int] = []

        for k in range(bp + bq):
            bits_to_add = columns[k] + incoming_carries
            outgoing_carries: List[int] = []

            # Reduce bits_to_add using full adders (3 bits -> 1 sum, 1 carry)
            # and half adders (2 bits -> 1 sum, 1 carry) until 1 bit remains
            while len(bits_to_add) > 1:
                if len(bits_to_add) >= 3:
                    x, y, z = bits_to_add.pop(0), bits_to_add.pop(0), bits_to_add.pop(0)
                    s, c = self._add_full_adder(cnf, vm, x, y, z)
                    bits_to_add.append(s)
                    outgoing_carries.append(c)
                else:
                    x, y = bits_to_add.pop(0), bits_to_add.pop(0)
                    s, c = self._add_half_adder(cnf, vm, x, y)
                    bits_to_add.append(s)
                    outgoing_carries.append(c)

            # Enforce the column bit against N
            col_bit = (N >> k) & 1
            if bits_to_add:
                final_sum_bit = bits_to_add[0]
                if col_bit == 1:
                    cnf.append([final_sum_bit])
                else:
                    cnf.append([-final_sum_bit])
            else:
                if col_bit != 0:
                    cnf.append([])  # Unsatisfiable

            incoming_carries = outgoing_carries

        # Any remaining carries after the last column must be 0
        for c in incoming_carries:
            cnf.append([-c])

        mapping = {
            "p_vars": p_vars,
            "q_vars": q_vars,
            "total_vars": vm.total_vars,
        }
        return cnf, mapping

    def _add_half_adder(self, cnf: CNF, vm: VarManager, x: int, y: int) -> Tuple[int, int]:
        """Half adder: s = x XOR y, c = x AND y."""
        s = vm.new_var()
        c = vm.new_var()

        # s <-> (x ^ y)
        cnf.append([-x, -y, -s])
        cnf.append([x, y, -s])
        cnf.append([x, -y, s])
        cnf.append([-x, y, s])

        # c <-> (x & y)
        cnf.append([-x, -y, c])
        cnf.append([x, -c])
        cnf.append([y, -c])

        return s, c

    def _add_full_adder(self, cnf: CNF, vm: VarManager, x: int, y: int, z: int) -> Tuple[int, int]:
        """Full adder: s = x XOR y XOR z, c = majority(x, y, z)."""
        s = vm.new_var()
        c = vm.new_var()

        # s <-> (x ^ y ^ z)
        cnf.append([-x, -y, -z, s])
        cnf.append([-x, y, z, s])
        cnf.append([x, -y, z, s])
        cnf.append([x, y, -z, s])
        cnf.append([x, y, z, -s])
        cnf.append([x, -y, -z, -s])
        cnf.append([-x, y, -z, -s])
        cnf.append([-x, -y, z, -s])

        if self.inject_malformed_carry:
            cnf.append([x, y, z, c])
        else:
            # c <-> (x&y | x&z | y&z)
            cnf.append([-x, -y, c])
            cnf.append([-x, -z, c])
            cnf.append([-y, -z, c])
            cnf.append([x, y, -c])
            cnf.append([x, z, -c])
            cnf.append([y, z, -c])

        return s, c

    def _add_less_than_or_equal(self, cnf: CNF, vm: VarManager, p_vars: List[int], q_vars: List[int]) -> None:
        """Enforce p <= q using fully deterministic comparator clauses."""
        # For p <= q with equal bit lengths:
        # We can construct eq_i <-> (p_i == q_i) and lt_i <-> (p_i < q_i)
        # Or enforce lexicographical order from MSB down
        n = len(p_vars)
        if n <= 1:
            return

        # ripple carry comparator from LSB up or prefix comparison:
        # let diff_k = p_k - q_k + borrow
        # Simpler: for each bit k from MSB down, if all higher bits are equal, then p_k <= q_k.
        # prefix_eq[k] <-> (p_{n-1}==q_{n-1}) & ... & (p_k==q_k)
        prefix_eq: List[int] = []
        for i in range(n):
            pi = p_vars[i]
            qi = q_vars[i]
            eq_i = vm.new_var()
            # eq_i <-> (pi == qi) <-> (pi & qi) | (~pi & ~qi)
            cnf.append([-pi, qi, -eq_i])
            cnf.append([pi, -qi, -eq_i])
            cnf.append([pi, qi, eq_i])
            cnf.append([-pi, -qi, eq_i])
            prefix_eq.append(eq_i)

        # For bit i from n-1 down to 1:
        # if (prefix_eq from n-1 down to i+1), then p_i <= q_i (i.e. ~p_i | q_i)
        for i in reversed(range(n)):
            if i == n - 1:
                # MSB: p[n-1] <= q[n-1]
                cnf.append([-p_vars[i], q_vars[i]])
            else:
                # antecedent: all higher bits equal
                higher_eqs = [prefix_eq[j] for j in range(i + 1, n)]
                # clause: -eq_{n-1} | ... | -eq_{i+1} | -p_i | q_i
                clause = [-eq for eq in higher_eqs] + [-p_vars[i], q_vars[i]]
                cnf.append(clause)


class CarrySaveAdderSATEncoder(SchoolbookSATEncoder):
    """Encodes p * q = N using Carry-Save Adder (CSA) Wallace-tree partial-product reduction."""

    def encode(self, N: int, bp: Optional[int] = None, bq: Optional[int] = None) -> Tuple[CNF, Dict[str, List[int]]]:
        """Encode p * q = N into CNF using Carry-Save tree architecture."""
        if N % 2 == 0:
            raise ValueError("Modulus N must be odd for semiprime factorization")

        nbits = N.bit_length()
        bp = bp or (nbits // 2)
        bq = bq or (nbits - bp)

        vm = VarManager()
        cnf = CNF()

        p_vars = vm.new_vars(bp)
        q_vars = vm.new_vars(bq)

        # Boundary constraints: factors are odd, so p_0 = 1, q_0 = 1
        cnf.append([p_vars[0]])
        cnf.append([q_vars[0]])

        # MSB constraints: p_{bp-1} = 1, q_{bq-1} = 1
        cnf.append([p_vars[bp - 1]])
        cnf.append([q_vars[bq - 1]])

        # Symmetry breaking: p <= q if bp == bq
        if self.symmetry_breaking and bp == bq:
            self._add_less_than_or_equal(cnf, vm, p_vars, q_vars)

        # Partial products: a_{i,j} = p_i AND q_j
        pp: Dict[Tuple[int, int], int] = {}
        for i in range(bp):
            for j in range(bq):
                if i == 0 and j == 0:
                    a = vm.new_var()
                    cnf.append([a])
                    pp[(i, j)] = a
                else:
                    a = vm.new_var()
                    pi = p_vars[i]
                    qj = q_vars[j]
                    cnf.append([-pi, -qj, a])
                    cnf.append([pi, -a])
                    cnf.append([qj, -a])
                    pp[(i, j)] = a

        total_cols = bp + bq
        columns: List[List[int]] = [[] for _ in range(total_cols)]
        for (i, j), var in pp.items():
            columns[i + j].append(var)

        # Carry-Save Tree reduction layers (3:2 compressors in parallel)
        while any(len(col) >= 3 for col in columns):
            next_columns: List[List[int]] = [[] for _ in range(total_cols)]
            for k in range(total_cols):
                col_bits = list(columns[k])
                while len(col_bits) >= 3:
                    x = col_bits.pop(0)
                    y = col_bits.pop(0)
                    z = col_bits.pop(0)
                    s, c = self._add_full_adder(cnf, vm, x, y, z)
                    next_columns[k].append(s)
                    if k + 1 < total_cols:
                        next_columns[k + 1].append(c)
                    else:
                        cnf.append([-c])
                next_columns[k].extend(col_bits)
            columns = next_columns

        # Final addition stage across columns
        incoming_carries: List[int] = []
        for k in range(total_cols):
            bits_to_add = columns[k] + incoming_carries
            outgoing_carries: List[int] = []

            while len(bits_to_add) > 1:
                if len(bits_to_add) >= 3:
                    x, y, z = bits_to_add.pop(0), bits_to_add.pop(0), bits_to_add.pop(0)
                    s, c = self._add_full_adder(cnf, vm, x, y, z)
                    bits_to_add.append(s)
                    outgoing_carries.append(c)
                else:
                    x, y = bits_to_add.pop(0), bits_to_add.pop(0)
                    s, c = self._add_half_adder(cnf, vm, x, y)
                    bits_to_add.append(s)
                    outgoing_carries.append(c)

            col_bit = (N >> k) & 1
            if bits_to_add:
                final_sum_bit = bits_to_add[0]
                if col_bit == 1:
                    cnf.append([final_sum_bit])
                else:
                    cnf.append([-final_sum_bit])
            else:
                if col_bit != 0:
                    cnf.append([])  # Unsatisfiable

            incoming_carries = outgoing_carries

        for c in incoming_carries:
            cnf.append([-c])

        mapping = {
            "p_vars": p_vars,
            "q_vars": q_vars,
            "total_vars": vm.total_vars,
            "architecture": "carry_save_tree",
        }
        return cnf, mapping

