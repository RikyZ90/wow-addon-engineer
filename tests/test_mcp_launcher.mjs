import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { once } from 'node:events';
import { mkdtempSync, mkdirSync, readFileSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { resolveEntrypoint } from '../scripts/mcp_launcher.mjs';

const launcher = fileURLToPath(new URL('../scripts/mcp_launcher.mjs', import.meta.url));

function fixture(t) {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'wae mcp launcher ')));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  return root;
}

function write(path, content = '') {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content);
  return path;
}

function installedPackage(root, metadata = {}) {
  write(join(root, 'package.json'), JSON.stringify({
    name: '@nighthawk42/wow-api-mcp',
    bin: { 'wow-api-mcp': 'dist/index.mjs' },
    ...metadata,
  }));
  return write(join(root, 'dist/index.mjs'), 'console.log("server fixture");\n');
}

test('missing installation fails without stdout or starting another command', t => {
  const root = fixture(t);
  write(join(root, 'npm.cmd'), '@echo should never execute');
  assert.throws(() => resolveEntrypoint({ PATH: root }), /not found/);
  const env = { ...process.env, PATH: root };
  delete env.WAE_WOW_API_MCP;
  const result = spawnSync(process.execPath, [launcher], { env, encoding: 'utf8' });
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /not found/);
});

test('invalid explicit override never falls back to an installed PATH server', t => {
  const root = fixture(t);
  write(join(root, 'wow-api-mcp.cmd'), 'untrusted shell code');
  installedPackage(join(root, 'node_modules/@nighthawk42/wow-api-mcp'));
  for (const override of ['', join(root, 'missing.mjs'), join(root, 'wow-api-mcp.cmd'), root]) {
    assert.throws(() => resolveEntrypoint({ PATH: root, WAE_WOW_API_MCP: override }), /must name an existing/);
  }
});

test('npm Windows global shim is located without executing its shell contents', t => {
  const root = fixture(t);
  write(join(root, 'wow-api-mcp.cmd'), 'throw if executed');
  const entry = installedPackage(join(root, 'node_modules/@nighthawk42/wow-api-mcp'));
  assert.equal(resolveEntrypoint({ PATH: root }), entry);
});

test('npm local .bin and Unix prefix layouts resolve installed entries', t => {
  const root = fixture(t);
  const localBin = join(root, 'local/node_modules/.bin');
  write(join(localBin, 'wow-api-mcp'), 'never execute a shell');
  const localEntry = installedPackage(join(root, 'local/node_modules/@nighthawk42/wow-api-mcp'));
  assert.equal(resolveEntrypoint({ PATH: localBin }), localEntry);
  const globalBin = join(root, 'prefix/bin');
  write(join(globalBin, 'wow-api-mcp'), 'never execute a shell');
  const globalEntry = installedPackage(join(root, 'prefix/lib/node_modules/@nighthawk42/wow-api-mcp'));
  assert.equal(resolveEntrypoint({ PATH: globalBin }), globalEntry);
});

test('npm shim package identity and bin containment are checked', t => {
  const root = fixture(t);
  write(join(root, 'wow-api-mcp.cmd'), 'never execute');
  const packageRoot = join(root, 'node_modules/@nighthawk42/wow-api-mcp');
  installedPackage(packageRoot, { name: 'unrelated/wow-api-mcp' });
  assert.throws(() => resolveEntrypoint({ PATH: root }), /not found/);
  installedPackage(packageRoot, { bin: { 'wow-api-mcp': '../escape.mjs' } });
  assert.throws(() => resolveEntrypoint({ PATH: root }), /escapes its package/);
});

test('POSIX npm symlink resolves and a bin symlink cannot escape its package', { skip: process.platform === 'win32' }, t => {
  const root = fixture(t);
  const packageRoot = join(root, 'prefix/lib/node_modules/@nighthawk42/wow-api-mcp');
  const entry = installedPackage(packageRoot);
  const bin = join(root, 'prefix/bin');
  mkdirSync(bin, { recursive: true });
  symlinkSync(entry, join(bin, 'wow-api-mcp'));
  assert.equal(resolveEntrypoint({ PATH: bin }), entry);
  rmSync(entry);
  symlinkSync(write(join(root, 'outside.mjs')), entry);
  assert.throws(() => resolveEntrypoint({ PATH: bin }), /escapes its package/);
});

test('direct entry with spaces preserves literal arguments, stdout and exit status', t => {
  const root = fixture(t);
  const entry = write(join(root, 'server entry.mjs'), 'console.log(JSON.stringify(process.argv.slice(2))); process.exitCode = 7;\n');
  const args = ['path with spaces', 'semi;colon', '$(echo nope)', '&', '%PATH%'];
  const result = spawnSync(process.execPath, [launcher, ...args], {
    env: { ...process.env, WAE_WOW_API_MCP: entry }, encoding: 'utf8',
  });
  assert.equal(result.status, 7);
  assert.equal(result.stderr, '');
  assert.deepEqual(JSON.parse(result.stdout), args);
});

test('stdio is preserved without launcher protocol output', t => {
  const root = fixture(t);
  const entry = write(join(root, 'echo.mjs'), 'process.stdin.pipe(process.stdout);\n');
  const input = '{"jsonrpc":"2.0","id":1,"method":"initialize"}\n';
  const result = spawnSync(process.execPath, [launcher], {
    env: { ...process.env, WAE_WOW_API_MCP: entry }, input, encoding: 'utf8',
  });
  assert.equal(result.status, 0);
  assert.equal(result.stdout, input);
  assert.equal(result.stderr, '');
});

for (const signal of ['SIGTERM', 'SIGINT']) {
  test(`POSIX ${signal} reaches the server in the launcher process`, {
    skip: process.platform === 'win32', timeout: 10000,
  }, async t => {
    const root = fixture(t);
    const marker = join(root, 'terminated');
    const entry = write(join(root, 'signal.mjs'), [
      "import { writeFileSync } from 'node:fs';",
      `process.on('${signal}', () => { writeFileSync(process.argv[2], 'stopped'); process.removeAllListeners('${signal}'); process.kill(process.pid, '${signal}'); });`,
      'console.log("ready");',
      'setInterval(() => {}, 1000);',
    ].join('\n'));
    const child = spawn(process.execPath, [launcher, marker], {
      env: { ...process.env, WAE_WOW_API_MCP: entry }, stdio: ['ignore', 'pipe', 'pipe'],
    });
    t.after(() => { if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL'); });
    await once(child.stdout, 'data');
    const exited = once(child, 'exit');
    child.kill(signal);
    assert.deepEqual(await exited, [null, signal]);
    assert.equal(readFileSync(marker, 'utf8'), 'stopped');
  });
}

test('the upstream server uses the launcher PID, so force-stop cannot orphan another process', { timeout: 10000 }, async t => {
  const root = fixture(t);
  const entry = write(join(root, 'pid.mjs'), 'console.log(process.pid); setInterval(() => {}, 1000);\n');
  const child = spawn(process.execPath, [launcher], {
    env: { ...process.env, WAE_WOW_API_MCP: entry }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  t.after(() => { if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL'); });
  const [output] = await once(child.stdout, 'data');
  const exited = once(child, 'exit');
  assert.equal(Number(output.toString().trim()), child.pid);
  child.kill('SIGKILL');
  await exited;
});
