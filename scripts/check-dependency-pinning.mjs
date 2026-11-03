import { readFileSync } from 'node:fs';

const manifests = ["packages/mcp/package.json"];
const exactVersion = /^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;
const failures = [];

for (const file of manifests) {
  const manifest = JSON.parse(readFileSync(new URL('../' + file, import.meta.url), 'utf8'));
  if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest)) throw new Error(file + ': manifest must be an object');
  for (const section of ['dependencies', 'devDependencies', 'optionalDependencies']) {
    const dependencies = manifest[section] ?? {};
    if (typeof dependencies !== 'object' || Array.isArray(dependencies)) throw new Error(file + ': invalid ' + section);
    for (const [name, value] of Object.entries(dependencies)) {
      if (typeof value === 'string' && /^(?:file|link|workspace):\S+$/.test(value)) continue;
      const version = typeof value === 'string' && value.startsWith('npm:') ? value.slice(value.lastIndexOf('@') + 1) : value;
      if (typeof version !== 'string' || !exactVersion.test(version)) failures.push(file + ': ' + section + '.' + name + ' must use an exact version');
    }
  }
}
if (failures.length) {
  console.error(failures.join('\n'));
  process.exitCode = 1;
} else {
  console.log('All direct dependencies use exact versions.');
}
