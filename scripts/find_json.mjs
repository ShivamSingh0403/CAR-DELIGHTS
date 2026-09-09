import fs from 'node:fs';
import path from 'node:path';

function findFiles(dir, filter, maxDepth = 4, currentDepth = 0) {
  if (currentDepth > maxDepth) return [];
  let results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === 'venv' || entry.name === '__pycache__') continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...findFiles(fullPath, filter, maxDepth, currentDepth + 1));
    } else if (filter(entry.name)) {
      results.push(fullPath);
    }
  }
  return results;
}

const jsonFiles = findFiles(process.cwd(), name => name.endsWith('.json'));
console.log('JSON files in project:');
jsonFiles.forEach(f => console.log(' ', f));
