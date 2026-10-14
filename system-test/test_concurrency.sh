#!/usr/bin/env bash
# Two overlapping requests to a CPU-bound `def` endpoint.
# Compare the timings between the single-worker and multi-worker setups.
set -u

BASE="http://localhost:8000/api/v1"
URL="$BASE/stress/cpu"
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
echo "----------------------------------------"

# Each curl writes `<json body> <time> <http code>` to its own file, read back after both finish
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

echo "----------------------------------------"
echo "Same-worker runs: $same_worker / $RUNS"
echo "Done."
