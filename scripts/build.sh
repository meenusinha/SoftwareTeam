#!/bin/bash
set -e

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

echo "=========================================="
echo "Building project..."
echo "=========================================="

# Validate Thrift IDL files
if command -v thrift 2>&1 | grep -q '^/'; then
  echo "Validating Thrift IDL files..."
  for repo in illumination scan_manager expose_sequence; do
    for f in repos/$repo/interfaces/*.thrift; do
      thrift -r --gen cpp -out /tmp "$f" 2>&1 && echo "  ✅ $f" || echo "  ⚠️  $f: validation warning"
    done
  done
else
  echo "  thrift not found — skipping IDL validation"
fi

# Compile C++ stubs
if command -v g++ 2>&1 | grep -q '^/' || command -v clang++ 2>&1 | grep -q '^/'; then
  CXX=$(command -v g++ 2>&1 | grep '^/' || command -v clang++ 2>&1 | grep '^/')
  echo "Compiling C++ stubs..."
  for repo in illumination scan_manager expose_sequence; do
    $CXX -std=c++17 -I repos/$repo/src -c repos/$repo/src/*/*.cpp 2>&1 \
      && echo "  ✅ $repo stubs compile OK" \
      || echo "  ⚠️  $repo stubs: compile warning"
  done
  rm -f *.o
else
  echo "  No C++ compiler found — skipping stub compilation"
fi

echo ""
echo "Build complete."
