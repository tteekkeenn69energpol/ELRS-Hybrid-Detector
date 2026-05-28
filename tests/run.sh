#!/usr/bin/env bash
# Reproducible Test/QA entry point for the 2D OS-CFAR Stage-1 suite.
#
#   1. Build the C-ABI wrapper as libcfar2d_c.so (links /src/cfar2d.cpp).
#   2. Run the Python driver (Pfa MC, ROC sweep, Pd vs SNR, throughput).
#   3. Post-process JSON → augment with analytic Pfa, render plot + markdown.
#   4. Copy report to the Obsidian logs directory.
#
# Approx wall time on i5-13600KF (20 threads): ~8 minutes.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_LOGS="${HERE}/../obsidian-vault/logs"

echo "[run.sh] 1/4  build libcfar2d_c.so"
"${HERE}/build_lib.sh"

echo "[run.sh] 2/4  run test_cfar2d.py"
cd "${HERE}"
python3 test_cfar2d.py

echo "[run.sh] 3/4  plot + report"
python3 plot_and_report.py

echo "[run.sh] 4/4  copy report → ${VAULT_LOGS}/test-results-2026-05-28.md"
mkdir -p "${VAULT_LOGS}"
cp "${HERE}/test-results.md" "${VAULT_LOGS}/test-results-2026-05-28.md"

echo "[run.sh] done."
