# Contributing to The Universal Playing Field

We are excited that you want to contribute to this 114-node discrete matrix framework! By submitting code, mathematical models, or bug fixes, you help build a computationally stable alternative to standard physics.

## 🚫 Hard Bounding Rules

Our framework operates on strict mathematical limits. Any code changes or community additions that violate these foundational constraints will be automatically rejected during the continuous integration (CI) audit:

1.  **No Gravitational Constants:** Any calculation relying on the physical gravitational constant ($G$), mass-induced spacetime curvature, or Einstein’s field equations will be stripped and rejected.
2.  **Discrete Processing Only:** All physical anomalies must be translated into discrete code refresh cycles, geometric refractions ($114/9$), or vector coordinate interactions ($3, 6, 9$).
3.  **Preserve Mirroring Streams:** Code additions must respect the boundary constraints of the mirroring potential streams ($987654321 \longleftrightarrow 0 \longleftrightarrow 123456789$).

## 🛠️ Step-by-Step Contribution Workflow

### 1. Sign the Contributor License Agreement (CLA)
Before you open a Pull Request, you must agree to the terms in `CLA.md`. 
*   **Automated Step:** Our repository uses a CLA tracking assistant. When you submit a pull request, the bot will check your git signature. If you haven't authorized it, simply click the prompt link in the PR comment section to electronically sign the contract.

### 2. Fork and Clone
Fork the repository to your own profile, create a branch containing a descriptive title (e.g., `feature/external-flux-refinement`), and clone it locally.

### 3. Maintain Code Architecture
Ensure all changes to the engine are structured cleanly inside the `UniversalMatrix` class structure within `matrix_calculator.py`. If you introduce variables adjusting ambient field vectors, they must accept custom input scalars to prevent closing the open-system network loop.

### 4. Run Tests Natively
Before committing your script modifications, ensure the demonstration engine fires cleanly without errors:
```bash
python matrix_calculator.py
```

### 5. Open Your Pull Request
Submit your branch changes back to our main tree. Ensure your PR description clearly notes:
*   The specific node interaction layer modified ($108$ core nodes vs. $6$ outer gate nodes).
*   A brief confirmation that no standard field equations or continuums were reintroduced.

Thank you for helping us scale this discrete open-system matrix framework!
