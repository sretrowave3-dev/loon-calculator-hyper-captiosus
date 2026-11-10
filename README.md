# Loon Calculator Hyper-Captiosus 🧮⚡

A hybrid calculator with a C computational backend and a Python graphical interface.

## Project architecture

```text
loon/
├── smart_calculator.py             # Python calculator and GUI
├── loon1.c                         # C computational engine source
├── control_pad.c                   # C control-pad source
├── append_modal.py                 # Modal extension utility
├── gen_plot.ps1                    # PowerShell plotting script
├── test_24.ps1                     # Automation and validation script
├── test_maclaurin.py               # Maclaurin series tests
└── scratch/                         # Experimental tests
```

Generated images, logs, personal profile data, and local application state are not listed here. Keep such files out of version control; review your repository and remove any sensitive files separately if they have already been committed.

## Setup

### 1. Get the project

Clone the repository and enter its directory:

```bash
git clone https://github.com/sretrowave3-dev/loon-calculator-hyper-captiosus.git
cd loon-calculator-hyper-captiosus
```

Alternatively, download the repository as a ZIP and extract it.

### 2. Install prerequisites

- Install Python 3.
- If you want to build or run the C components, install a C compiler such as GCC or Clang.
- PowerShell is only needed for the `.ps1` scripts.

### 3. Start the Python application

Run:

```bash
python smart_calculator.py
```

On systems where Python 3 is invoked as `python3`, use:

```bash
python3 smart_calculator.py
```

### 4. Build the C components (optional)

From the repository directory, compile the C sources with GCC:

```bash
gcc loon1.c -o loon1
 gcc control_pad.c -o control_pad
```

Run the resulting program using `./loon1` or `./control_pad` on macOS/Linux. On Windows, run the generated `.exe` files from the terminal. If a source file requires additional libraries or compiler options, add those according to its code and your platform.

### 5. Run tests (optional)

Run the Python test suite files directly, for example:

```bash
python test_maclaurin.py
```

The PowerShell scripts can be run in PowerShell:

```powershell
.\test_24.ps1
.\gen_plot.ps1
```

## Privacy and generated files

Files such as JSON state/profile files, images, and logs can contain personal or usage information. Do not commit them unless they are intentionally sanitized and needed by the project. If they were committed previously, deleting them from the current README or working tree does not remove them from Git history; remove sensitive data from history and rotate any exposed credentials as appropriate.
