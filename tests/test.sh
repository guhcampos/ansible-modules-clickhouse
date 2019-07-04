#!/bin/bash

export PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && cd .. && pwd)"


function run_tests() {
  echo "DROP DATABASE testdb" | clickhouse-client 2>/dev/null
  [[ $(python3 -m clickhouse_db test-create.json | jq .changed) == true  ]] && echo "." || echo "X"
  [[ $(python3 -m clickhouse_db test-create.json | jq .changed) == false ]] && echo "." || echo "X"
  [[ $(python3 -m clickhouse_db test-delete.json | jq .changed) == true  ]] && echo "." || echo "X"
  [[ $(python3 -m clickhouse_db test-delete.json | jq .changed) == false ]] && echo "." || echo "X"
  [[ $(python3 -m clickhouse_db test-create.json | jq .changed) == true  ]] && echo "." || echo "X"
  [[ $(python3 -m clickhouse_db test-delete.json | jq .changed) == true  ]] && echo "." || echo "X"
  [[ $(python3 -m clickhouse_db test-delete.json | jq .changed) == false ]] && echo "." || echo "X"
  [[ $(python3 -m clickhouse_db test-create.json | jq .changed) == true  ]] && echo "." || echo "X"
}

function cleanup() {
  echo "cleaning up"
  echo "DROP DATABASE testdb" | clickhouse-client 2>/dev/null
  docker stop clickhouse-ansible-test > /dev/null
  docker rm clickhouse-ansible-test > /dev/null
}

trap cleanup EXIT
echo "bringing up container"
docker run -d -p 9000:9000 --name clickhouse-ansible-test yandex/clickhouse-server > /dev/null
sleep 1
echo "testing"
run_tests
