#!/usr/bin/env bash
set -euo pipefail

candidate="${1:?Pass the candidate image name}"
candidate_sha="${2:?Pass the candidate revision}"
previous="${3:-}"
previous_sha="${4:-}"
mkdir -p evidence

deploy() {
    local stage="$1" image="$2" revision="$3" id result=0
    export RELAY_IMAGE="$image"
    printf '\n== %s / %s ==\n' "$stage" "$revision"
    docker compose up -d --no-build --force-recreate --wait --wait-timeout 21 \
        2>&1 | tee "evidence/$stage-compose.log" || return 1
    id="$(docker compose ps -q relay)" || return 1
    [[ -n "$id" ]] || return 1
    python -m pytest -q test_container.py --hosts="docker://$id" \
        --junitxml="evidence/$stage-testinfra.xml" || result=1
    python probe.py "${RELAY_HOST_PORT:-8291}" "$revision" || result=1
    return "$result"
}

snapshot() {
    RELAY_IMAGE="$1" docker compose logs --no-color > "evidence/$2-container.log" 2>&1 || true
}

if deploy candidate "$candidate" "$candidate_sha"; then
    snapshot "$candidate" candidate
    printf 'Accepted image: %s\n' "$candidate_sha"
    exit 0
fi

snapshot "$candidate" candidate
printf 'Rejected image: %s\n' "$candidate_sha"
if [[ -z "$previous" || -z "$previous_sha" ]]; then
    echo 'No previous successful release'
    exit 1
fi

if ! docker image inspect "$previous" > /dev/null 2>&1; then
    docker pull "$previous" 2>&1 | tee evidence/rollback-pull.log
fi

if deploy restored "$previous" "$previous_sha"; then
    printf 'Rollback verified: %s\n' "$previous_sha"
else
    printf 'Rollback failed: %s\n' "$previous_sha"
fi
snapshot "$previous" restored
exit 1
