# quantum-circuit-converter

Converts RevLib / QLib files to OpenQASM 2.0 format

## Usage

```python
from quantum_circuit_converter import QuantumCircuitConverter

file_path = 'path/input/circuit'
output_dir = 'path/output/dir'

result = (
    QuantumCircuitConverter(file_path)
        .to_openqasm()      # convert file format to openqasm 2.0
        .decompose()        # decompose Toffoli gates to IBM primitive gates
        .save('output_dir') # save result file in given directory
)
```
