#!/usr/bin/env node
import { spawn } from 'node:child_process'
import { createRequire } from 'node:module'
import path from 'node:path'

/** Canonical hosted MCP endpoint. Keep in sync with server.json remotes. */
export const MCP_URL = 'https://app.contracko.com/mcp'

if (process.argv.includes('--help') || process.argv.includes('-h')) {
	console.log(`Usage: contracko-mcp [mcp-remote options]

Connect a local stdio client to ${MCP_URL} with OAuth.
CLM (clm_*): add, import and manage contracts without Parser credits.
Contracko Parser (parser_*): separate bulk document processing; uses Parser credits;
not needed to add contracts to your contract register.

--help, -h  Show this help without connecting.`)
	process.exit(0)
}

const require = createRequire(import.meta.url)
const remoteRoot = path.dirname(require.resolve('mcp-remote/package.json'))
const proxy = path.join(remoteRoot, 'dist', 'proxy.js')

export function buildProxyArgv(extraArgs = process.argv.slice(2)) {
	return [proxy, MCP_URL, ...extraArgs]
}

// Always start. npm/npx invoke this file through a symlink, so comparing
// process.argv[1] to import.meta.url without realpath would no-op.
const child = spawn(process.execPath, buildProxyArgv(), { stdio: 'inherit' })

for (const signal of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
	process.on(signal, () => {
		child.kill(signal)
	})
}

child.on('exit', (code, signal) => {
	if (signal) {
		process.kill(process.pid, signal)
		return
	}
	process.exit(code ?? 1)
})
