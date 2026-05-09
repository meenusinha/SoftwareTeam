#!/usr/bin/env bash
# Full agentic animation demo — runs all agents through all states

REPO="$(cd "$(dirname "$0")/.." && pwd)"
set_state() { bash "$REPO/scripts/set-agent-state.sh" "$1" "$2" "$3"; echo ">>> $1 / $2 — $3"; sleep 2; }

echo "=== STEP 1: IT Agent — Verify Tools ==="
set_state it thinking    "Verifying tools..."
set_state it typing      "Checking git and gh CLI..."
set_state it approved    "Tools verified!"
set_state it handingoff  "Handing off to Product Owner..."

echo "=== STEP 2: Product Owner — Requirements ==="
set_state product-owner thinking   "Gathering requirements..."
set_state product-owner waiting    "Waiting for user input..."
set_state product-owner typing     "Writing user story..."
set_state product-owner reviewing  "Reviewing user story..."
set_state product-owner handingoff "Handing off to Cost Analyst..."

echo "=== STEP 3: Cost Analyst — Cost Estimate ==="
set_state cost-analyst thinking   "Analysing scope..."
set_state cost-analyst reviewing  "Estimating costs..."
set_state cost-analyst typing     "Writing cost estimate..."
set_state cost-analyst handingoff "Handing off to Architect..."

echo "=== STEP 4: Architect — Design ==="
set_state architect thinking   "Designing the system..."
set_state architect typing     "Writing technical specs..."
set_state architect reviewing  "Reviewing design..."
set_state architect handingoff "Handing off to IT Agent..."

echo "=== STEP 5: IT Agent — Project Setup ==="
set_state it thinking   "Setting up project environment..."
set_state it typing     "Installing deps and creating scripts..."
set_state it approved   "Project setup complete!"
set_state it handingoff "Handing off to Developer..."

echo "=== STEP 6: Developer — Implementation ==="
set_state developer thinking   "Planning implementation..."
set_state developer typing     "Writing code..."
set_state developer reviewing  "Reviewing implementation..."
set_state developer reworking  "Fixing issues..."
set_state developer approved   "Implementation complete!"
set_state developer handingoff "Handing off to Tester..."

echo "=== STEP 7: Tester — Validation ==="
set_state tester thinking   "Planning tests..."
set_state tester typing     "Writing and running tests..."
set_state tester reviewing  "Reviewing test results..."
set_state tester reworking  "Retesting after fixes..."
set_state tester approved   "All tests passed!"
set_state tester handingoff "Handing off to IT for release..."

echo "=== STEP 8: IT Agent — Release ==="
set_state it thinking   "Building release..."
set_state it typing     "Packaging release artifacts..."
set_state it approved   "Release ready!"
set_state it handingoff "Handing off to Product Owner..."

echo "=== STEP 9: Product Owner — Acceptance ==="
set_state product-owner reviewing   "Final acceptance review..."
set_state product-owner approved    "Accepted!"
set_state product-owner celebrating "Task complete!"

echo "=== ANIMATION COMPLETE ==="
