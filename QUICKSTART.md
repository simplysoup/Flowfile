# Quickstart

## Prerequisites

- Python 3.12 (managed via `uv`)
- Node.js 20+ (managed via `fnm`)
- Rust toolchain (`rustup`) - for Tauri desktop builds only

## Install Dependencies

### Python (backend)

```powershell
uv venv --python 3.12 .venv
uv pip install -e .
```

### Node (frontend)

```powershell
cd flowfile_frontend
npm install
cd ..
```

## Run in Dev Mode (Electron-like)

The `start-dev.ps1` script starts both the backend (port 63578) and the Vite frontend dev server (port 55800):

```powershell
.\start-dev.ps1
```

Then open `http://localhost:55800` in your browser.

To run the services separately:

```powershell
# Terminal 1 - Backend
.venv\Scripts\python.exe -m flowfile_core.main

# Terminal 2 - Frontend
cd flowfile_frontend
npm run dev:web -- --port 55800
```

The frontend proxies `/api` requests to the backend on port 63578.

## Build Desktop Binary (Tauri)

The full build pipeline compiles the Python backend into standalone executables via PyInstaller, stages them as Tauri sidecars, and produces an installer.

### Step 1: Install build dependencies

```powershell
uv pip install pyinstaller
```

Or with Poetry (if available):

```powershell
poetry install --with build
```

### Step 2: Build Python services

```powershell
.venv\Scripts\python.exe -m build_backends.main
```

This produces `services_dist/` containing:
- `flowfile_core.exe` - the backend API server
- `flowfile_worker.exe` - the compute worker
- `_internal/` - shared Python runtime and all dependencies

### Step 3: Stage sidecars for Tauri

```powershell
.venv\Scripts\python.exe tools/rename_sidecar.py
```

Copies executables into `flowfile_frontend/src-tauri/binaries/<name>-<target-triple>`.

### Step 4: Build Tauri app

```powershell
cd flowfile_frontend
npm run build
```

The installer is output to `flowfile_frontend/src-tauri/target/release/bundle/`.

### All-in-one (with Make)

If `make` is available:

```powershell
make all
```

This runs: `install_python_deps` -> `build_python_services` -> `rename_sidecars` -> `sign_sidecars` -> `build_tauri_app` -> `generate_key`.

## Smoke Test Built Binaries

After `make build_python_services` or step 2 above:

```powershell
# Start the built binaries
Start-Process ./services_dist/flowfile_core.exe
Start-Process ./services_dist/flowfile_worker.exe

# Wait a few seconds, then test
Invoke-WebRequest http://127.0.0.1:63578/docs
Invoke-WebRequest http://127.0.0.1:63579/docs
```

Both should return HTTP 200.

## Default Ports

| Service | Port |
|---------|------|
| flowfile_core (backend API) | 63578 |
| flowfile_worker (compute) | 63579 |
| Vite dev server (start-dev.ps1) | 55800 |
| Vite dev server (npm run dev:web) | 8080 |
