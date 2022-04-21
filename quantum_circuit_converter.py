import sys


class QuantumCircuitConverter:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.format    = file_path.split('.')[-1]
        self.supported_format = {'qlib', 'revlib', 'qasm'}

        with open(file_path, 'r') as file:
            self.lines = file.readlines()


    def to_string(self) -> str:
        return '\n'.join(self.lines)


    def to_openqasm(self):
        if self.format not in self.supported_format:
            print(f'warning: unsupported format - "{self.format}"')
            sys.exit()

        if self.format == 'qlib':
            return self.__qlib_to_openqasm()
        elif self.format == 'revlib':
            return self.__revlib_to_openqasm()
        return self


    def decompose(self):
        if self.format == 'qasm':
            return (
                self
                    # .__openqasm_decompose_c3x()
                    .__openqasm_decompose_ccx()
            )
        return self


    def __revlib_to_openqasm(self):
        if self.format != 'revlib':
            print('called wrong function...')
            sys.exit()

        result = ['OPENQASM 2.0;', 'include "qelib1.inc";']

        n_qubits = 0
        qreg_map = {}

        gate_map = {
            't2': 'cx',
            't3': 'ccx',
            't4': 'c3x'
        }

        for line in self.lines:
            words = line.strip().split()

            if len(words) == 0:
                continue

            op = words[0]

            if op == '#':
                continue

            if op == '.numvars':
                n_qubits = int(words[1])
                result.append(f'qreg q[{n_qubits}];')
                result.append(f'creg c[{n_qubits}];')

            if op == '.variables':
                for i, qreg_name in enumerate(words[1:]):
                    qreg_map[qreg_name] = f'q[{i}]'

            if op == '.constants':
                for i, val in enumerate(words[1]):
                    if val == '1':
                        result.append(f'x q[{i}]')
            
            if op in gate_map:
                operands = [qreg_map[word] for word in words if word != op]
                inst = ' '.join([gate_map[op], ','.join(operands)]) + ';'
                result.append(inst)
        
        self.lines = result
        self.format = 'qasm'

        return self


    def __qlib_to_openqasm(self):
        if self.format != 'qlib':
            print('called wrong function...')
            sys.exit()

        result = ['OPENQASM 2.0;', 'include "qelib1.inc";']

        n_qubits = 0
        qreg_map = {}
        qreg_idx = 0

        gate_map = {
            'X':        'x',
            'Z':        'z',
            'H':        'h',
            'CNOT':     'cx',
            'Toffoli':  'ccx'
        }

        for line in self.lines:
            words = line.strip().split()

            if len(words) == 0:
                continue

            op = words[0]

            if op == '#':
                continue

            if op == '.qubit':
                n_qubits = int(words[1])
                result.append(f'qreg q[{n_qubits}];')
                result.append(f'creg c[{n_qubits}];')

            if op == 'qubit':
                if qreg_idx >= n_qubits:
                    print('qlib error')
                    sys.exit()

                qreg_name = words[1]

                if qreg_name in qreg_map:
                    print('qlib error')
                    sys.exit()

                qreg_map[qreg_name] = f'q[{qreg_idx}]'
                qreg_idx += 1
                
            if op in gate_map:
                operands = [qreg_map[word] for word in words if word != op]
                inst = ' '.join([gate_map[op], ','.join(operands)]) + ';'
                result.append(inst)

        self.lines = result
        self.format = 'qasm'

        return self


    def __openqasm_decompose_c3x(self):
        if self.format != 'qasm':
            print('called wrong function...')
            sys.exit()

        # TODO: add c3x decompositon here
        print('warning: `__openqasm_decompose_c3x` not implemented yet')

        return self


    def __openqasm_decompose_ccx(self):
        if self.format != 'qasm':
            print('called wrong function...')
            sys.exit()

        result = []

        for line in self.lines:
            operator, operand = line.split(' ')

            if operator == 'ccx':
                a, b, c = operand.rstrip(';').split(',')
                decomposed = '\n'.join([
                    f'h {c};', 
                    f'cx {b},{c};', f'tdg {c};', 
                    f'cx {a},{c};', f't {c};', 
                    f'cx {b},{c};', f'tdg {c};', 
                    f'cx {a},{c};', f't {b};', f't {c};', f'h {c};', 
                    f'cx {a},{b};', f't {a};', f'tdg {b};', 
                    f'cx {a},{b};'
                ])
                result.append(decomposed)

            else:
                result.append(line)

        self.lines = result

        return self


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python main.py <file_path>')
        sys.exit()

    file_path = sys.argv[1]

    result = (
        QuantumCircuitConverter(file_path)
            .to_openqasm()
            .decompose()
            .to_string()
    )

    print(result)
    
