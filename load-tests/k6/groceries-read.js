/*
 * Read-path load test for the grocery API (public GET endpoints, no auth needed).
 * Thresholds mirror the roadmap target (Topic 16): p95 < 100ms.
 * Run via docker/grocery-management-k6.yml
 */
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://host.docker.internal:8000';
const API = `${BASE_URL}/api/v1/groceries`;
const HEADERS = { 'Accept-Encoding': 'gzip' }; // behave like a browser

export const options = {
  scenarios: {
    // most traffic: opening a single grocery
    detail: {
      executor: 'ramping-vus',
      exec: 'detail',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 20 }, // ramp up
        { duration: '1m', target: 20 },  // steady
        { duration: '15s', target: 0 },  // ramp down
      ],
    },
    // fewer users loading the full list in parallel
    list: {
      executor: 'constant-vus',
      exec: 'list',
      vus: 2,
      duration: '1m45s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{name:detail}': ['p(95)<100'],
    'http_req_duration{name:list}': ['p(95)<100'],
  },
};

// runs once before the test: collect ids to request in the detail scenario
export function setup() {
  const res = http.get(`${API}/`, { headers: HEADERS, tags: { name: 'setup' } });
  if (res.status !== 200) {
    throw new Error(`setup: list request failed with ${res.status}, is the API running at ${BASE_URL}?`);
  }
  const ids = res.json('data').slice(0, 500).map((g) => g.id);
  if (ids.length === 0) {
    throw new Error('setup: no groceries found, seed the database first');
  }
  return { ids };
}

export function detail({ ids }) {
  const id = ids[Math.floor(Math.random() * ids.length)];
  const res = http.get(`${API}/${id}`, { headers: HEADERS, tags: { name: 'detail' } });
  check(res, { 'detail 200': (r) => r.status === 200 });
  sleep(1);
}

export function list() {
  const res = http.get(`${API}/`, { headers: HEADERS, tags: { name: 'list' } });
  check(res, { 'list 200': (r) => r.status === 200 });
  sleep(1);
}
