#!/usr/bin/env node
import { readFileSync, realpathSync, statSync } from 'node:fs';
import { delimiter, dirname, extname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const packageName = '@nighthawk42/wow-api-mcp';

function isFile(path) {
  try {
    return statSync(path).isFile();
  } catch (error) {
    if (error.code === 'ENOENT' || error.code === 'ENOTDIR') return false;
    throw error;
  }
}

function isJavaScript(path) {
  return ['.js', '.mjs'].includes(extname(path).toLowerCase());
}

function packageEntry(root) {
  const manifest = join(root, 'package.json');
  if (!isFile(manifest)) return null;
  const metadata = JSON.parse(readFileSync(manifest, 'utf8'));
  if (metadata.name !== packageName) return null;
  const bin = metadata.bin?.['wow-api-mcp'];
  if (typeof bin !== 'string' || !isJavaScript(bin)) return null;
  root = realpathSync(root);
  const entry = resolve(root, bin);
  const outside = path => {
    const location = relative(root, path);
    return location === '..' || location.startsWith(`..${sep}`) || isAbsolute(location);
  };
  if (outside(entry)) throw new Error('Installed wow-api-mcp entry point escapes its package directory.');
  if (!isFile(entry)) return null;
  const actual = realpathSync(entry);
  if (outside(actual)) throw new Error('Installed wow-api-mcp entry point escapes its package directory.');
  return actual;
}

export function resolveEntrypoint(env = process.env) {
  if (env.WAE_WOW_API_MCP !== undefined) {
    const entry = resolve(env.WAE_WOW_API_MCP);
    if (!isJavaScript(entry) || !isFile(entry)) {
      throw new Error('WAE_WOW_API_MCP must name an existing .js or .mjs server entry point.');
    }
    return realpathSync(entry);
  }
  for (const directory of (env.PATH ?? '').split(delimiter).filter(Boolean)) {
    const shimDirectory = resolve(directory.replace(/^"(.*)"$/, '$1'));
    for (const suffix of ['', '.cmd', '.bat', '.ps1']) {
      const shim = join(shimDirectory, `wow-api-mcp${suffix}`);
      if (!isFile(shim)) continue;
      const actual = realpathSync(shim);
      const roots = [
        resolve(dirname(actual), '..'),
        join(shimDirectory, 'node_modules', packageName),
        resolve(shimDirectory, '..', packageName),
        resolve(shimDirectory, '..', 'lib', 'node_modules', packageName),
      ];
      for (const root of roots) {
        const entry = packageEntry(root);
        if (entry) return entry;
      }
    }
  }
  throw new Error(`User-installed ${packageName} was not found. Set WAE_WOW_API_MCP to its installed dist/index.js.`);
}

async function main() {
  const [major, minor] = process.versions.node.split('.').map(Number);
  if (major < 20 || (major === 20 && minor < 11)) throw new Error('wow-api-mcp requires Node.js 20.11 or newer.');
  const entry = resolveEntrypoint();
  process.argv = [process.execPath, entry, ...process.argv.slice(2)];
  await import(pathToFileURL(entry).href);
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => {
    console.error(`WoW Addon Engineer: ${error.message}`);
    process.exitCode = 1;
  });
}
