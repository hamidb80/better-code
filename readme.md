# Better Code
an experiment to make reading code experience better.

it rewrite the tokens and syntax to visual appealing symbols (based on pre-defined rules). 

## Applicatons

originaly created for lowering mental barrier to read and understand source code.

### Quantum computing
you see `|ψ⟩ = α|0⟩ + β|1⟩` Instead of `ket_psi = alpha * ket_0 + beta * ket_1`

### Linear Algebra
```py
# Matrix multiplication
C = A.dot(B)
# Your tool shows:
C = A × B   or   C = A·B

# Element-wise product (Hadamard)
C = A.hadamard(B)
# Becomes:
C = A ⊙ B

# Kronecker product
C = A.kronecker(B)
# Becomes:
C = A ⊗ B

# Transpose
A_T = A.transpose()
# Becomes:
Aᵀ

# Conjugate transpose (Hermitian)
A_H = A.H()
# Becomes:
Aᴴ   or   A†

# Inverse
A_inv = A.inv()
# Becomes:
A⁻¹

# Pseudo-inverse
A_pinv = A.pinv()
# Becomes:
A⁺
```


## Programming Language Support
only Python for now.

## Inspirations
* Latex: where you write something and get something else.
* BQN: simple and math familiar syntax
* 