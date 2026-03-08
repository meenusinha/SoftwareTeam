#!/usr/bin/env node

/**
 * Author Revision Script
 *
 * Called after peer reviewers request changes.
 * Collects all reviewer inline comments, prompts the LLM (acting as the
 * original author agent) to address them, and writes the revised file
 * contents back to disk. The workflow then commits the changes.
 *
 * Usage:
 *   node author-revision.js \
 *     --agent <agent-type> \
 *     --pr-number <number> \
 *     --repo <owner/repo> \
 *     --pr-details-file <path>
 *
 * Environment variables: LLM_PROVIDER, LLM_API_KEY, GITHUB_TOKEN
 */

'use strict';

const { Octokit } = require('octokit');
const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// CLI arg parsing
// ---------------------------------------------------------------------------
function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {};
  for (let i = 0; i < args.length; i += 2) {
    parsed[args[i].replace(/^--/, '')] = args[i + 1];
  }
  return parsed;
}

// ---------------------------------------------------------------------------
// Collect review feedback from the PR
// ---------------------------------------------------------------------------
async function collectReviewFeedback(octokit, owner, repo, prNumber) {
  // Inline review comments (on specific lines / files)
  const inlineRes = await octokit.rest.pulls.listReviewComments({
    owner,
    repo,
    pull_number: prNumber,
    per_page: 100
  });

  // General PR issue comments that contain a "CHANGES REQUESTED" verdict
  const issueRes = await octokit.rest.issues.listComments({
    owner,
    repo,
    issue_number: prNumber,
    per_page: 100
  });

  const changesRequestedPattern = /\*\*(.+?) Agent Review\*\*/;
  const summaryComments = issueRes.data.filter(
    c => changesRequestedPattern.test(c.body) && c.body.includes('🔴 **CHANGES REQUESTED**')
  );

  return { inlineComments: inlineRes.data, summaryComments };
}

// ---------------------------------------------------------------------------
// Build the revision prompt
// ---------------------------------------------------------------------------
function constructRevisionPrompt(agentType, prDetails, inlineComments, summaryComments) {
  const agentLabel = agentType
    .split('-')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');

  // Format inline comments grouped by file
  const byFile = {};
  for (const c of inlineComments) {
    const key = c.path;
    if (!byFile[key]) byFile[key] = [];
    byFile[key].push({ line: c.original_line || c.line, body: c.body });
  }

  const inlineSection = Object.entries(byFile)
    .map(([file, comments]) => {
      const lines = comments
        .map(c => `  Line ${c.line}: ${c.body.replace(/\*\*🤖.*?\*\*\n\n/, '').substring(0, 300)}`)
        .join('\n');
      return `### ${file}\n${lines}`;
    })
    .join('\n\n');

  const summarySection = summaryComments
    .map(c => {
      // Strip the markdown heading and agent boilerplate, keep the meat
      return c.body
        .replace(/^## 🤖.*?\n\n/, '')
        .replace(/---\n\*Automated.*\*\s*$/, '')
        .trim();
    })
    .join('\n\n---\n\n');

  // Build per-file current content section
  const filesSection = prDetails.files
    .map(f => {
      let content = '(content not available)';
      try {
        const abs = path.join(process.cwd(), f.filename);
        if (fs.existsSync(abs)) content = fs.readFileSync(abs, 'utf8');
      } catch (_) {}
      return `### ${f.filename}\n\`\`\`\n${content}\n\`\`\``;
    })
    .join('\n\n');

  return `You are acting as the **${agentLabel} Agent** who authored this pull request.
Peer reviewers have requested changes. Your job is to address every piece of feedback and produce revised file contents.

## PR Title
${prDetails.title}

## Reviewer Summary Feedback
${summarySection || '(see inline comments)'}

## Inline Review Comments (per file)
${inlineSection || '(none)'}

## Current File Contents
${filesSection}

## Your Task

For **each file that has review comments**, produce the full revised content that addresses all the feedback.
Output ONLY the revised files using this exact format — one block per file, no other text:

FILE: <relative/path/to/file>
<<<CONTENT>>>
<full revised file content>
<<<END>>>

Rules:
- Output ALL lines of the file, not just changed sections.
- Address every inline comment and every issue raised in the summary feedback.
- Do not remove existing functionality unless a reviewer explicitly asked you to.
- Only output files that you are actually changing — skip unchanged files.
- Do not add explanations outside the FILE blocks.
`;
}

// ---------------------------------------------------------------------------
// Call LLM (reuse provider modules from automated-review.js)
// ---------------------------------------------------------------------------
async function callLLM(prompt, agentType) {
  const provider = (process.env.LLM_PROVIDER || 'openai').toLowerCase();
  const providerMap = { claude: 'anthropic', 'azure-openai': 'azure' };
  const normalized = providerMap[provider] || provider;

  let mod;
  try {
    mod = require(`./providers/${normalized}.js`);
  } catch {
    console.error(`Unsupported LLM provider: ${provider}`);
    process.exit(1);
  }
  return mod.callLLM(prompt, agentType);
}

// ---------------------------------------------------------------------------
// Parse LLM output into { filePath, content } pairs
// ---------------------------------------------------------------------------
function parseRevisedFiles(llmOutput) {
  const results = [];
  const fileBlockRegex = /FILE:\s*(.+?)\n<<<CONTENT>>>\n([\s\S]*?)<<<END>>>/g;
  let match;
  while ((match = fileBlockRegex.exec(llmOutput)) !== null) {
    const filePath = match[1].trim();
    const content = match[2]; // preserve exact content (no trim — may matter for some files)
    results.push({ filePath, content });
  }
  return results;
}

// ---------------------------------------------------------------------------
// Write revised files to disk
// ---------------------------------------------------------------------------
function applyRevisions(revisedFiles) {
  for (const { filePath, content } of revisedFiles) {
    const abs = path.join(process.cwd(), filePath);
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    fs.writeFileSync(abs, content);
    console.log(`  ✏️  Revised: ${filePath}`);
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  const args = parseArgs();

  if (!args.agent || !args['pr-number'] || !args.repo || !args['pr-details-file']) {
    console.error('Usage: node author-revision.js --agent <type> --pr-number <num> --repo <owner/repo> --pr-details-file <path>');
    process.exit(1);
  }
  if (!process.env.LLM_API_KEY) { console.error('LLM_API_KEY is required'); process.exit(1); }
  if (!process.env.GITHUB_TOKEN) { console.error('GITHUB_TOKEN is required'); process.exit(1); }

  const agentType   = args.agent;
  const prNumber    = parseInt(args['pr-number'], 10);
  const [owner, repo] = args.repo.split('/');
  const prDetails   = JSON.parse(fs.readFileSync(args['pr-details-file'], 'utf8'));

  console.log(`\n========================================`);
  console.log(`Author Revision`);
  console.log(`========================================`);
  console.log(`Agent : ${agentType}`);
  console.log(`PR    : #${prNumber}`);
  console.log(`Repo  : ${args.repo}`);
  console.log(`========================================\n`);

  const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

  console.log('Collecting review feedback…');
  const { inlineComments, summaryComments } = await collectReviewFeedback(octokit, owner, repo, prNumber);
  console.log(`  Inline comments : ${inlineComments.length}`);
  console.log(`  Summary reviews : ${summaryComments.length}`);

  if (inlineComments.length === 0 && summaryComments.length === 0) {
    console.log('No review feedback found — nothing to revise.');
    return;
  }

  console.log('\nBuilding revision prompt…');
  const prompt = constructRevisionPrompt(agentType, prDetails, inlineComments, summaryComments);

  console.log('Calling LLM for revision…');
  const llmOutput = await callLLM(prompt, agentType);

  console.log('\nParsing revised files from LLM output…');
  const revisedFiles = parseRevisedFiles(llmOutput);
  console.log(`  Files to revise : ${revisedFiles.length}`);

  if (revisedFiles.length === 0) {
    console.warn('LLM did not produce any FILE blocks. Raw output:\n', llmOutput.substring(0, 500));
    console.log('Nothing written to disk.');
    return;
  }

  console.log('\nApplying revisions…');
  applyRevisions(revisedFiles);

  console.log('\n✅ Author revision complete!');
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
