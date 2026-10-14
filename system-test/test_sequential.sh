#!/usr/bin/env bash
# /stress/cpu/sequential: an `async def` with no await, so it BLOCKS the event loop.
# Three checks, see docs/project-staff/phase-5-vertical-scaling-simulations.md §5:
#   1. one request alone
#   2. two overlapping requests (same worker or different workers?)
#   3. is /health blocked while a long (?tasks=8) request runs?
# Compare the output between the single-worker and multi-worker setups.
set -u

BASE="http://localhost:8000/api/v1"
URL="$BASE/stress/cpu/sequential"
RUNS="${1:-5}"
WAIT_TIMEOUT=60 # seconds to wait for the API after a restart

# Wait until the API answers (`up -d` returns before uvicorn is ready)
printf "Waiting for API"
for ((t = 0; t < WAIT_TIMEOUT; t++)); do
  curl -sf -o /dev/null "$BASE/health/" && break
  printf "."
  sleep 1
done
echo
if ! curl -sf -o /dev/null "$BASE/health/"; then
  echo "API not ready after ${WAIT_TIMEOUT}s. Check: docker compose -f docker-compose.dev.yml logs backend"
  exit 1
fi

echo "Setup: $(curl -s "$BASE/health/")"
echo "Target: $URL  (runs: $RUNS)"

# Each curl writes `<json body> <time> <http code>` to its own file, read back after it finishes
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

# Sets PID and DESC ("<time>s (HTTP <code>, pid <pid>)") from one result file.
# Called without $(...) so the globals reach the caller.
describe() {
  local body time code
  read -r body time code < "$1"
  PID=$(sed -n 's/.*"worker_pid":\([0-9]*\).*/\1/p' <<< "$body")
  DESC="${time}s (HTTP $code, pid ${PID:-?})"
}

echo "----------------------------------------"
echo "1. One request alone"
for i in $(seq 1 "$RUNS"); do
  curl -s -w " %{time_total} %{http_code}" "$URL" > "$TMP_DIR/a"
  describe "$TMP_DIR/a"
  echo "run $i  $DESC"
done

echo "----------------------------------------"
echo "2. Two requests ~50 ms apart"
same_worker=0
for i in $(seq 1 "$RUNS"); do
  curl -s -w " %{time_total} %{http_code}" "$URL" > "$TMP_DIR/a" &
  sleep 0.05
  curl -s -w " %{time_total} %{http_code}" "$URL" > "$TMP_DIR/b" &
  wait

  describe "$TMP_DIR/a"; a=$DESC; pid_a=$PID
  describe "$TMP_DIR/b"; b=$DESC; pid_b=$PID
  if [[ -n "$pid_a" && "$pid_a" == "$pid_b" ]]; then
    verdict="SAME worker"
    ((same_worker++))
  else
    verdict="different workers"
  fi
  echo "run $i  A: $a  B: $b  -> $verdict"
done
echo "Same-worker runs: $same_worker / $RUNS"

echo "----------------------------------------"
echo "3. /health while a ?tasks=8 request runs"
for i in $(seq 1 "$RUNS"); do
  curl -s -w " %{time_total} %{http_code}" "$URL?tasks=8" > "$TMP_DIR/a" &
  sleep 0.2
  health=$(curl -s -o /dev/null -w "%{time_total}s (HTTP %{http_code})" "$BASE/health/")
  wait

  describe "$TMP_DIR/a"
  echo "run $i  health waited $health  long request: $DESC"
done

echo "----------------------------------------"
echo "Done."
