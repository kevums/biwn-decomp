// Real local inference through the plugin handler, with a mock UI controller.
// This cannot establish native Chat selection, rendering or user cancellation.
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { homedir } from 'node:os';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const installedBundle = join(homedir(), '.lmstudio/extensions/plugins/local/visible-local-team/dist/index.js');
const { handleTeam, LMStudioClient, Chat } = createRequire(import.meta.url)(installedBundle);
const installedBundleSha256 = createHash('sha256').update(await readFile(installedBundle)).digest('hex');
const lms = join(homedir(), '.lmstudio/bin/lms');
const catalogResult = spawnSync(lms, ['ps', '--json'], { encoding: 'utf8' });
if (catalogResult.status !== 0) throw Error(catalogResult.stderr);
const catalog = JSON.parse(catalogResult.stdout);
if (catalog.length !== 1 || catalog[0].identifier !== 'advertising-scholar' || catalog[0].status !== 'idle') {
  throw Error('The restored daily model must be the only loaded model and idle; do not load a second copy.');
}
const out = join(root, 'verification/native-team-handler-check', new Date().toISOString().replaceAll(':', '-'));
await mkdir(out, { recursive: true });
const domain = process.argv[2] || 'game';
if (!['game', 'advertising'].includes(domain)) throw Error('Choose game or advertising');
const question = process.argv[3] || (domain === 'game'
  ? 'Explain what the building 532 route proves in under 120 words. Include checkpoint origin, inherited repair, DSP/audio coverage and whether it is standalone.'
  : 'Using Lee & Koo (2016), create a hypothetical 12-minute undergraduate activity in at most 180 words. Ask students to identify Experiment 1 high/low endorser-product congruence stimuli, explain a product-category alternative explanation, and propose a follow-up that better separates fit from category. Give a question asking all three and three distinct one-point rubric criteria. Use contiguous elapsed-time intervals totaling 12 minutes. Cite actual source basename/chunk and PDF page for empirical facts. Label the follow-up hypothetical and disclose remaining endorser-identity effects. Do not invent findings or sales effects.');
const history = Chat.from([{ role: 'user', content: question }]);
const client = new LMStudioClient();
const model = await client.llm.model('advertising-scholar');
const controller = new AbortController();
const blocks = [];
const config = { domain, showPrompts: true, roleMaxTokens: 6000 };
const proof = { status: 'starting', interface: 'Mock native UI controller with real LM Studio local SDK model',
  native_UI_verified: false, native_Chat_verified: false, domain, question, directory: out, model_catalog: catalog, blocks };
proof.installed_bundle = installedBundle;
proof.installed_bundle_sha256 = installedBundleSha256;
const save = () => writeFile(join(out, 'receipt.json'), JSON.stringify(proof, null, 2) + '\n');
await save();
try {
  await handleTeam({
    getPluginConfig() { return { get(key) { return config[key]; } }; },
    pullHistory: async () => history,
    abortSignal: controller.signal,
    guardAbort() { if (controller.signal.aborted) throw Error('Aborted'); },
    tokenSource: async () => model,
    setSenderName: async name => { proof.sender = name; },
    needsNaming: async () => true,
    suggestName: async name => { proof.suggested_name = name; },
    createContentBlock(options) {
      const block = { options, text: '' }; blocks.push(block);
      return { appendText(text) { block.text += text; },
        async pipeFrom(prediction) {
          for await (const fragment of prediction) block.text += fragment.content;
          const result = await prediction;
          block.stats = result.stats;
          return result;
        } };
    },
  });
  const intro = blocks.find(b => b.options.style.label === 'Team workflow');
  const sessionPath = intro.text.match(/Full prompts and responses: ([^\n]+)/)?.[1];
  if (!sessionPath) throw Error('No auditable plugin session path');
  const session = JSON.parse(await readFile(join(sessionPath, 'session.json'), 'utf8'));
  const expectedRoles = session.workflow === 'copyediting' ? ['Copy Editor', 'Copy Reviewer'] :
    (domain === 'game' ? ['Analyst', 'Restorer', 'Reviewer'] : ['Researcher', 'Educator', 'Reviewer']);
  if(domain==='advertising'&&session.roles.some(r=>r.role==='Researcher anchor repair'))expectedRoles.splice(1,0,'Researcher anchor repair');
  if (session.roles.length !== expectedRoles.length || session.roles.some(r => r.stats.stopReason !== 'eosFound')) throw Error('Incomplete role outputs');
  if(domain==='advertising'&&session.workflow!=='copyediting'){
    const briefs=session.roles.filter(r=>r.anchor_validation);
    if(!briefs.length||briefs.at(-1).anchor_validation.errors.length)throw Error('No validated source brief reached lesson writing');
  }
  for (const [index, role] of expectedRoles.entries()) {
    const prompt = await readFile(join(sessionPath, `${index + 1}-${role}-prompt.txt`), 'utf8');
    const response = await readFile(join(sessionPath, `${index + 1}-${role}-response.txt`), 'utf8');
    if (blocks.find(b => b.options.style.label === role + ' prompt')?.text !== prompt) throw Error('Prompt block mismatch');
    if (blocks.find(b => b.options.style.label === role)?.text !== response) throw Error('Response block mismatch');
  }
  const answerBlocks = blocks.filter(b => expectedRoles.includes(b.options.style.label));
  if (answerBlocks.some((b, i) => b.options.includeInContext !== (i === expectedRoles.length - 1))) throw Error('Only final response may enter follow-up context');
  Object.assign(proof, { status: 'real_local_roles_and_prompt_blocks_complete_semantic_review_pending', workflow: session.workflow, session: sessionPath,
    generation_stats: session.roles.map(r => ({ role: r.role, stats: r.stats })), semantic_review: 'pending',
    scope: 'Actual local model generations through the exact installed plugin source handler. UI controller is a test double, so native Chat rendering/selection/cancellation remains unverified. No native conversation file created or modified.' });
} catch (error) {
  Object.assign(proof, { status: 'terminal_failed', error: String(error) });
  process.exitCode = 1;
} finally {
  await save();
  const pointer = proof.workflow === 'copyediting' ? 'native-copyediting-team-handler-current.json' :
    (domain === 'game' ? 'native-team-handler-check-current.json' : 'native-advertising-team-handler-current.json');
  await writeFile(join(root, 'verification/' + pointer), JSON.stringify(proof, null, 2) + '\n');
}
console.log(out, proof.status);
