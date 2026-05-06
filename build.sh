#!/usr/bin/env bash
# Build script for X360Forge (Linux)
# Usage: bash build.sh
# Installs all dependencies, builds native tools, and bundles the app.

set -e

# ---------------------------------------------------------------------------
# 1. System dependencies
# ---------------------------------------------------------------------------
echo "==> Installing system dependencies..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y \
        python3-tk \
        cmake \
        gcc \
        libcurl4-openssl-dev \
        zlib1g-dev \
        python3-pip
elif command -v dnf &>/dev/null; then
    sudo dnf install -y \
        python3-tkinter \
        cmake \
        gcc \
        libcurl-devel \
        zlib-devel \
        python3-pip
elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm \
        tk \
        cmake \
        gcc \
        curl \
        zlib \
        python-pip
else
    echo "WARNING: Unknown package manager — install python3-tk, cmake, gcc, libcurl-dev, zlib-dev manually if the build fails."
fi

# Rust / cargo
if ! command -v cargo &>/dev/null; then
    echo "==> Installing Rust toolchain via rustup..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path
fi
# Ensure cargo is on PATH regardless of when it was installed
# shellcheck source=/dev/null
[ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env"

# PyInstaller
echo "==> Installing PyInstaller..."
if ! command -v pyinstaller &>/dev/null; then
    pip3 install --quiet --break-system-packages pyinstaller
fi
export PATH="$HOME/.local/bin:$PATH"

# Ensure submodules are present
echo "==> Updating git submodules..."
git submodule update --init --recursive

# ---------------------------------------------------------------------------
# 2. Build native tools
# ---------------------------------------------------------------------------
echo "==> Building extract-xiso (XISO extraction tool)..."
cd x_tool/extract-xiso-src
cmake -B build -S .
cmake --build build --parallel "$(nproc)"
cp build/extract-xiso ../extract-xiso
cd ../..

echo "==> Building iso2god (ISO to GOD converter)..."
cd x_tool/iso2god-rs
cargo build --release
cp target/release/iso2god ../iso2god
cd ../..

echo "==> Building god2iso (GOD to ISO converter)..."
cd x_tool/god2iso-rs
cargo build --release
cp target/release/god2iso ../god2iso
cd ../..

echo "==> Building abgx360 (ISO fix/verify tool)..."
cd x_tool/abgx360-src
./configure --prefix="$(pwd)/install"
make -j"$(nproc)"
cp abgx360 ../abgx360
cd ../..

# ---------------------------------------------------------------------------
# 3. Bundle the Python application
# ---------------------------------------------------------------------------
echo "==> Bundling Python application with PyInstaller..."
pyinstaller \
    --onefile \
    --add-data "x_tool:x_tool" \
    --add-data "Images:Images" \
    --add-data "x_ISO:x_ISO" \
    --name "X360Forge" \
    main.pyw

echo ""
echo "Build complete."
echo ""
echo "  Run the app:    python3 main.pyw"
echo "  Or use bundle:  ./dist/X360Forge"
echo ""
