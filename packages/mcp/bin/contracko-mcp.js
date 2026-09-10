#!/usr/bin/env node
import { spawn } from 'node:child_process'
import { createRequire } from 'node:module'
import path from 'node:path'

/** Canonical hosted MCP endpoint. Keep in sync with server.json remotes. */
export const MCP_URL = 'https://app.contracko.com/mcp'

const require = createRequire(import.meta.url)
const remoteRoot = path.dirname(require.resolve('mcp-remote/package.json'))
const proxy = path.join(remoteRoot, 'dist', 'proxy.js')

export function buildProxyArgv(extraArgs = process.argv.slice(2)) {
	return [proxy, MCP_URL, ...extraArgs]
}

// Always start. npm/npx invoke this file through a symlink, so comparing
// process.argv[1] to import.meta.url without realpath would no-op.
const child = spawn(process.execPath, buildProxyArgv(), { stdio: 'inherit' })
child.on('exit', (code, signal) => {
	if (signal) {
		process.kill(process.pid, signal)
		return
	}
	process.exit(code ?? 1)
})
