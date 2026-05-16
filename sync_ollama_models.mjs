import { readFile, writeFile } from 'fs/promises';
import { homedir } from 'os';
import { join } from 'path';

const OLLAMA_URL = 'http://192.168.1.15:11434';
const CONFIG_PATH = join(homedir(), '.config', 'opencode', 'opencode.json');

try {
  const res = await fetch(`${OLLAMA_URL}/api/tags`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  const models = data.models ?? [];

  if (models.length === 0) {
    console.error('No models found in Ollama');
    process.exit(1);
  }

  console.log(`Found ${models.length} models:`);
  const modelEntries = {};
  for (const m of models) {
    const name = m.name;
    modelEntries[name] = { name };
    console.log(`  - ${name}`);
  }

  const config = {
    $schema: 'https://opencode.ai/config.json',
    plugin: ['opencode-skill-creator'],
    provider: {
      ollama: {
        npm: '@ai-sdk/openai-compatible',
        options: { baseURL: `${OLLAMA_URL}/v1` },
        models: modelEntries,
      },
    },
  };

  await writeFile(CONFIG_PATH, JSON.stringify(config, null, 2) + '\n', 'utf-8');
  console.log(`\nConfig written to ${CONFIG_PATH}`);
  console.log(`Restart OpenCode to use the new models.`);
} catch (err) {
  console.error(`Cannot connect to Ollama at ${OLLAMA_URL}:`, err.message);
  process.exit(1);
}
