#!/usr/bin/env node

/**
 * Automated Peer Review Script
 *
 * This script uses LLM API to review pull requests as different agent roles
 * (Product Owner, Architect, Tester, Developer, IT).
 *
 * Usage:
 *   node automated-review.js \
 *     --agent <agent-type> \
 *     --pr-number <number> \
 *     --repo <owner/repo> \
 *     --pr-details-file <path>
 *
 * Environment variables:
 *   LLM_PROVIDER - Provider name: openai, anthropic, gemini, azure, cohere, mistral (default: openai)
 *   LLM_API_KEY - API key for your LLM provider
 *   AZURE_OPENAI_ENDPOINT - Required for Azure OpenAI (e.g., https://your-resource.openai.azure.com)
 *   GITHUB_TOKEN - Required for GitHub API
 *
 * Supported LLM Providers:
 *   - openai: OpenAI GPT-4o (default)
 *   - anthropic/claude: Anthropic Claude Sonnet 4
 *   - gemini: Google Gemini Pro
 *   - azure/azure-openai: Azure OpenAI
 *   - cohere: Cohere Command R Plus
 *   - mistral: Mistral Large
 */

const { Octokit } = require('octokit');
const fs = require('fs');
const path = require('path');

// Read agent .md files for context
function loadAgentContext(agentType) {
  const agentFilePath = path.join(process.cwd(), 'ai-assistants', 'agents', `${agentType}-agent.md`);
  
  if (fs.existsSync(agentFilePath)) {
    return fs.readFileSync(agentFilePath, 'utf8');
  }
  
  console.warn(`Warning: Agent file not found at ${agentFilePath}`);
  return null;
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {};

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    const value = args[i + 1];
    parsed[key] = value;
  }

  return parsed;
}

// Agent review prompts and checklists
const AGENT_PROMPTS = {
  'product-owner': {
    role: 'Product Owner Agent',
    title: 'Customer-Facing Requirements Lead and Backlog Manager',
    expertise: [
      'Requirements gathering and user story creation',
      'Acceptance criteria definition',
      'Stakeholder communication',
      'Project coordination and workflow management'
    ],
    checklist: [
      'User stories are clear with well-defined acceptance criteria',
      'Requirements align with project goals',
      'Documentation is complete and user-facing',
      'Deliverables match acceptance criteria',
      'Work follows proper workflow sequence',
      'All agent handoffs are properly documented',
      'PR description is clear and complete',
      'Changes meet business requirements'
    ],
    focus: 'requirements alignment, acceptance criteria, documentation completeness, workflow compliance'
  },

  'product-owner': {
    role: 'Product Owner Agent',
    title: 'Customer-Facing Requirements Lead and Backlog Manager',
    expertise: [
      'Requirements gathering and user story creation',
      'Acceptance criteria definition',
      'Stakeholder communication',
      'Project coordination and workflow management'
    ],
    checklist: [
      'User stories are clear with well-defined acceptance criteria',
      'Requirements align with project goals',
      'Documentation is complete and user-facing',
      'Deliverables match acceptance criteria',
      'Work follows proper workflow sequence',
      'All agent handoffs are properly documented',
      'PR description is clear and complete',
      'Changes meet business requirements'
    ],
    focus: 'requirements alignment, acceptance criteria, documentation completeness, workflow compliance'
  },

  'architect': {
    role: 'Architect Agent',
    title: 'System Architect and Design Lead',
    expertise: [
      'Software Architecture and Design (OO principles, SOLID, UML)',
      'Design Patterns (GoF): Creational, Structural, Behavioral',
      'Architectural Patterns: Layered, Hexagonal, Clean, Microservices',
      'Interface and API design'
    ],
    checklist: [
      'Implementation follows EDS specifications exactly',
      'Interfaces and APIs are correctly implemented',
      'Design patterns are appropriate and correctly implemented',
      'SOLID principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion',
      'Component boundaries are clear, low coupling, high cohesion',
      'Architecture is maintainable and extensible',
      'Platform support (Linux, macOS) is correctly handled',
      'No architectural violations or design flaws'
    ],
    focus: 'design adherence, SOLID principles, design patterns, architecture quality, interface correctness'
  },

  'tester': {
    role: 'Tester Agent',
    title: 'Quality Assurance and Testing Specialist',
    expertise: [
      'Testing frameworks (gtest, Catch2, JUnit, pytest)',
      'Test design and automation',
      'Quality gates and metrics',
      'Integration and system testing'
    ],
    checklist: [
      'Code is structured for testability',
      'Unit tests are present for all new/modified code',
      'Test coverage is adequate (>80% target)',
      'Tests follow AAA pattern (Arrange, Act, Assert)',
      'Edge cases and error paths are tested',
      'Tests are clear, independent, repeatable, and fast',
      'Integration points are properly tested',
      'Quality gates are met (no test failures, adequate coverage)'
    ],
    focus: 'testability, test coverage, test quality, edge cases, quality gates'
  },

  'developer': {
    role: 'Developer Agent',
    title: 'Software Developer and Implementation Specialist',
    expertise: [
      'Object-Oriented Programming (OOP principles, SOLID, design patterns)',
      'Code quality and clean code principles',
      'Testing (TDD, unit testing, mocking)',
      'Modern practices (Git workflow, code review)'
    ],
    checklist: [
      'Code is clean, readable, and maintainable',
      'Naming is clear and descriptive',
      'Functions are small and focused (<50 lines)',
      'No code duplication (DRY principle)',
      'Logic is correct and efficient',
      'Error handling is comprehensive',
      'Resource cleanup is proper (RAII, destructors)',
      'No code smells (long methods, large classes, deep nesting, magic numbers)',
      'Best practices: const-correctness, smart pointers, thread safety',
      'Memory management is safe'
    ],
    focus: 'code quality, implementation correctness, best practices, no code smells'
  }
};

// Check if this agent has previously reviewed this PR
async function getPreviousReview(octokit, repo, prNumber, agentType) {
  const [owner, repoName] = repo.split('/');
  const agent = AGENT_PROMPTS[agentType];

  try {
    // Get all reviews for this PR
    const { data: reviews } = await octokit.rest.pulls.listReviews({
      owner,
      repo: repoName,
      pull_number: prNumber
    });

    // Find reviews from this agent (by checking review body for agent marker)
    const agentMarker = `**${agent.role} Review**`;
    const previousReviews = reviews.filter(review =>
      review.body && review.body.includes(agentMarker)
    );

    if (previousReviews.length === 0) {
      return null;
    }

    // Get the most recent review from this agent
    const latestReview = previousReviews[previousReviews.length - 1];

    // Get review comments (inline comments)
    const { data: comments } = await octokit.rest.pulls.listReviewComments({
      owner,
      repo: repoName,
      pull_number: prNumber,
      review_id: latestReview.id
    });

    return {
      review: latestReview,
      comments: comments,
      state: latestReview.state
    };
  } catch (error) {
    console.error('Error fetching previous review:', error.message);
    return null;
  }
}

// Construct review prompt for LLM
function constructReviewPrompt(agentType, prDetails, previousReview = null, isRework = false) {
  const agent = AGENT_PROMPTS[agentType];
  const agentContext = loadAgentContext(agentType);

  const prompt = `You are the ${agent.title} reviewing a pull request in the YourProject repository.

**Your Role**: ${agent.role}

${agentContext ? `
## Your Complete Agent Definition

${agentContext}

---

` : ''}

**Your Expertise**:
${agent.expertise.map(e => `- ${e}`).join('\n')}

**Review Focus**: ${agent.focus}

## Pull Request Details

**Title**: ${prDetails.title}

**Description**:
${prDetails.body}

**Changed Files** (${prDetails.files.length} files):
${prDetails.files.map(f => `- ${f.filename} (+${f.additions}/-${f.deletions})`).join('\n')}

${previousReview && isRework ? `
## 🔄 REWORK RE-REVIEW MODE

The developer has reworked this PR to address your previous review. **This is the final review pass — no further rework will be requested.**

**Your Previous Review** (${previousReview.state}):
${previousReview.comments.length > 0 ? previousReview.comments.map((c, i) => `
${i + 1}. **${c.path}:${c.line}**
   ${c.body.replace(/\*\*🤖.*?\*\*\n\n/, '')}
`).join('\n') : '(No inline comments in previous review)'}

**Your Task**:
1. Check each of your previous concerns against the new commits
2. For each: note whether it was RESOLVED or still present (remarks only — no blocking)
3. Add any new observations as inline remarks (optional, informational only)
4. End with a mandatory approval — this is the final pass

**Required Response Format**:

### Rework Assessment
[1-2 sentences: overall assessment of how well the rework addressed your concerns]

### Previous Issues Status
${previousReview.comments.map((c, i) => `Issue #${i + 1} (${c.path}:${c.line}):
- Status: ✅ RESOLVED / ⚠️ PARTIALLY ADDRESSED / ❌ STILL PRESENT (remark only — not blocking)
- Verification: [how you verified it / what remains]`).join('\n\n')}

### Rework Remarks
[Any new inline comments as observations on the rework — format same as below. Write "None" if no remarks.]

INLINE_COMMENT: path/to/file.ext:123
**[Severity: Minor]** [Observation title]
[Brief note — informational, not blocking]

### Decision
[You MUST write this exact line — no other option:]
✅ **APPROVED** - Rework reviewed. [1 sentence summary: e.g. "Critical issues were addressed." / "Some concerns remain but approval is granted for this pass."]

` : previousReview ? `
## 🔄 RE-REVIEW MODE

**IMPORTANT**: You have previously reviewed this PR and requested changes. The developer has pushed new commits to address your feedback.

**Your Previous Review** (${previousReview.state}):
${previousReview.comments.length > 0 ? previousReview.comments.map((c, i) => `
${i + 1}. **${c.path}:${c.line}**
   ${c.body.replace(/\*\*🤖.*?\*\*\n\n/, '')}
`).join('\n') : '(No inline comments in previous review)'}

**Your Task for Re-Review**:
1. Check if the new commits address each of your previous concerns
2. For each previous comment:
   - If ADDRESSED: Mark as resolved (mention "RESOLVED" in response)
   - If NOT ADDRESSED: Explain why and keep requesting changes
3. Do NOT post new comprehensive reviews or new issues
4. Focus ONLY on verifying your previous feedback was addressed

**Response Format for Re-Review**:

### Re-Review Summary
[Brief statement: "All concerns addressed" OR "Some concerns remain"]

### Previous Issues Status
[For each previous issue:]
Issue #1 (${previousReview.comments[0]?.path || 'file'}:${previousReview.comments[0]?.line || 'line'}):
- Status: ✅ RESOLVED / ❌ NOT RESOLVED
- Verification: [How you verified it was fixed / Why it's not fixed]

### Decision
[Write EXACTLY one of these:]
✅ **APPROVED** - All previous concerns have been addressed.
🔴 **CHANGES REQUESTED** - Some concerns remain unaddressed.

` : `
## Your Task

Review this pull request thoroughly using your expertise and the following checklist:`}

## Code Changes

${prDetails.files.map(f => `
### File: ${f.filename}
Status: ${f.status}
Changes: +${f.additions}/-${f.deletions}

\`\`\`diff
${f.patch || '(Binary file or no patch available)'}
\`\`\`
`).join('\n')}

${isRework ? `
**IMPORTANT — REWORK REVIEW RULES**:
- Follow the "Required Response Format" above exactly
- Check every previous issue and mark it RESOLVED / PARTIALLY ADDRESSED / STILL PRESENT
- Inline remarks are optional and informational only (Severity: Minor)
- The Decision MUST be ✅ **APPROVED** — no other option is allowed
- Your approval line MUST contain a brief summary sentence after the dash
` : `
**Review Checklist**:
${agent.checklist.map((item, i) => `${i + 1}. ${item}`).join('\n')}

## Review Guidelines

1. **Be thorough**: Check every item on your checklist
2. **Be specific**: Point out exact issues with line numbers/file names
3. **Be constructive**: Provide actionable feedback
4. **Be fair**: Acknowledge good work, but don't lower standards
5. **Focus on your expertise**: Apply your domain knowledge

## CRITICAL CONSTRAINTS

**Comment Prioritization** - Focus ONLY on these critical areas:
1. **Design Issues**: Architecture violations, design pattern misuse, SOLID violations, poor abstractions
2. **Functionality Issues**: Logic errors, incorrect implementations, broken features, edge case failures
3. **Consistency Issues**: Inconsistent with project standards, naming conventions, code style, patterns
4. **Clean Code Issues**: Code smells, hard-to-maintain code, duplication, excessive complexity

**Comment Limit**: Maximum **10 inline comments** per review
- Prioritize the MOST critical issues first
- Focus on issues that have the biggest impact on code quality
- Skip minor formatting or trivial issues if limit is reached
- Every comment must be actionable and important

**Severity Guidelines**:
- **Critical**: Breaks functionality, major design flaw, security issue, violates core principles
- **Major**: Significant code quality issue, maintainability problem, important best practice violation
- **Minor**: Small improvement, stylistic preference, minor inconsistency

## Response Format

Provide your review in this exact format:

### Summary
[1-2 sentences: overall assessment]

### Inline Comments
[Provide MAXIMUM 10 inline comments focusing on the most critical issues]
[Prioritize: Design > Functionality > Consistency > Clean Code]
[Format: Each comment MUST start with "INLINE_COMMENT:" followed by file path and line number]
[If no inline comments, write "None"]

INLINE_COMMENT: path/to/file.ext:123
**[Severity: Critical/Major/Minor]** [Issue title]
[Detailed explanation of the problem and recommendation for fixing it]

[Repeat for each critical issue - MAX 10 COMMENTS TOTAL]

### Positive Aspects
[List good practices observed, or write "None notable" if basic]
- [What was done well]

### Decision
[Write EXACTLY one of these two options:]
✅ **APPROVED** - This PR meets all quality standards for ${agent.role}.
🔴 **CHANGES REQUESTED** - This PR requires changes before approval.

**IMPORTANT**:
- Be strict but fair
- Only approve if ALL checklist items pass
- If there are any Critical or Major issues, you MUST request changes
- Minor issues alone can be approved with suggestions
- Apply SOLID principles and design pattern knowledge rigorously
- For inline comments, always specify the exact file path and line number where the issue exists
- Line numbers should reference the new file content (after changes), not the diff
- **CRITICAL**: Provide MAXIMUM 10 inline comments - prioritize the most impactful issues
- Focus ONLY on: Design, Functionality, Consistency, and Clean Code issues
- Skip minor/trivial issues to stay within the 10-comment limit
`}`;

  return prompt;
}

// Call LLM API for review
async function callLLMForReview(agentType, prDetails, previousReview = null, isRework = false) {
  const provider = (process.env.LLM_PROVIDER || 'openai').toLowerCase();
  const prompt = constructReviewPrompt(agentType, prDetails, previousReview, isRework);

  console.log(`\nUsing LLM Provider: ${provider}`);
  console.log(`Calling ${provider} API as ${agentType}...`);

  // Map provider aliases
  const providerMap = {
    'claude': 'anthropic',
    'azure-openai': 'azure'
  };
  const normalizedProvider = providerMap[provider] || provider;

  // Dynamically load provider module
  let providerModule;
  try {
    providerModule = require(`./providers/${normalizedProvider}.js`);
  } catch (error) {
    const supportedProviders = ['openai', 'anthropic', 'gemini', 'azure', 'cohere', 'mistral', 'copilot'];
    throw new Error(
      `Unsupported LLM provider: ${provider}\n` +
      `Supported providers: ${supportedProviders.join(', ')}\n` +
      `Error: ${error.message}`
    );
  }

  // Call the provider's LLM function
  const review = await providerModule.callLLM(prompt, agentType);

  console.log(`Review received (${review.length} chars)`);

  return review;
}

// Parse inline comments from review text
function parseInlineComments(reviewText) {
  const comments = [];
  const lines = reviewText.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Look for INLINE_COMMENT: path/to/file:line
    const match = line.match(/^INLINE_COMMENT:\s*(.+):(\d+)\s*$/);

    if (match) {
      const path = match[1].trim();
      const lineNum = parseInt(match[2]);

      // Collect the comment body (lines after INLINE_COMMENT: until next section or empty line)
      let commentBody = '';
      let j = i + 1;

      while (j < lines.length) {
        const nextLine = lines[j];

        // Stop at next INLINE_COMMENT or section header
        if (nextLine.startsWith('INLINE_COMMENT:') ||
            nextLine.startsWith('###') ||
            (nextLine.trim() === '' && lines[j + 1]?.startsWith('INLINE_COMMENT:'))) {
          break;
        }

        commentBody += nextLine + '\n';
        j++;
      }

      commentBody = commentBody.trim();

      if (commentBody && path && lineNum > 0) {
        comments.push({
          path: path,
          line: lineNum,
          body: commentBody
        });

        console.log(`  Parsed inline comment: ${path}:${lineNum}`);
      }

      i = j - 1; // Skip to after this comment
    }
  }

  return comments;
}

// Extract summary from review text (everything before the ### Decision section).
// Works for both regular reviews (### Summary / ### Positive Aspects) and
// rework reviews (### Rework Assessment / ### Previous Issues Status / ### Rework Remarks).
function extractSummary(reviewText) {
  const decisionIdx = reviewText.indexOf('### Decision');
  const decisionMatch = reviewText.match(/### Decision\s*([\s\S]*?)$/);

  // Take everything before ### Decision, strip raw INLINE_COMMENT: blocks
  // (those are rendered as inline comments separately)
  const beforeDecision = decisionIdx >= 0
    ? reviewText.substring(0, decisionIdx)
    : reviewText;

  const summaryText = beforeDecision
    .replace(/^INLINE_COMMENT:.*$/mg, '')   // remove INLINE_COMMENT: header lines
    .replace(/\n{3,}/g, '\n\n')             // collapse extra blank lines
    .trim();

  let summary = '';
  if (summaryText) {
    summary += summaryText + '\n\n';
  }
  if (decisionMatch) {
    summary += '### Decision\n' + decisionMatch[1].trim();
  }

  return summary.trim();
}

// Resolve review threads for addressed issues using GitHub GraphQL API.
// isRework=true resolves ALL threads unconditionally (forced approval pass).
async function resolveReviewThreads(octokit, repo, prNumber, reviewText, previousReview, isRework = false) {
  if (!previousReview || !previousReview.comments || previousReview.comments.length === 0) {
    return;
  }

  const [owner, repoName] = repo.split('/');

  // Check if review text indicates issues were resolved
  const resolvedPattern = /Status:\s*✅\s*RESOLVED/gi;
  const matches = reviewText.matchAll(resolvedPattern);
  const resolvedCount = Array.from(matches).length;

  console.log(`  Found ${resolvedCount} issues marked as RESOLVED in re-review`);

  // In rework mode the PR is force-approved, so resolve ALL threads regardless
  // of whether they're marked RESOLVED, PARTIALLY ADDRESSED, or STILL PRESENT.
  const shouldResolveAll = isRework || resolvedCount > 0 || reviewText.includes('All previous concerns have been addressed');
  if (!shouldResolveAll) return;

  // Build a set of database IDs from the previous review's inline comments
  const previousCommentIds = new Set(previousReview.comments.map(c => String(c.id)));

  // Fetch all review threads via GraphQL to get their node IDs (needed for the mutation)
  let threads = [];
  try {
    const result = await octokit.graphql(`
      query GetReviewThreads($owner: String!, $repo: String!, $prNumber: Int!) {
        repository(owner: $owner, name: $repo) {
          pullRequest(number: $prNumber) {
            reviewThreads(first: 50) {
              nodes {
                id
                isResolved
                comments(first: 1) {
                  nodes { databaseId }
                }
              }
            }
          }
        }
      }
    `, { owner, repo: repoName, prNumber });
    threads = result.repository.pullRequest.reviewThreads.nodes;
  } catch (err) {
    console.error(`  ⚠️  GraphQL query for review threads failed: ${err.message}`);
  }

  let resolved = 0;
  for (const thread of threads) {
    if (thread.isResolved) continue;
    const firstId = thread.comments.nodes[0]?.databaseId;
    if (!firstId || !previousCommentIds.has(String(firstId))) continue;

    try {
      await octokit.graphql(`
        mutation ResolveThread($threadId: ID!) {
          resolveReviewThread(input: { threadId: $threadId }) {
            thread { id isResolved }
          }
        }
      `, { threadId: thread.id });
      resolved++;
      console.log(`  ✅ Resolved thread ${thread.id}`);
    } catch (err) {
      console.error(`  ⚠️  Could not resolve thread ${thread.id}: ${err.message}`);
    }
  }

  console.log(`  Resolved ${resolved} conversation thread(s).`);
}

// Parse review decision (APPROVED or CHANGES REQUESTED)
function parseReviewDecision(reviewText) {
  if (reviewText.includes('✅ **APPROVED**')) {
    return 'APPROVE';
  } else if (reviewText.includes('🔴 **CHANGES REQUESTED**')) {
    return 'REQUEST_CHANGES';
  } else {
    console.warn('Could not parse decision, defaulting to COMMENT');
    return 'COMMENT';
  }
}

// Post review with inline comments using GitHub Pull Request Review API
async function postPullRequestReview(octokit, repo, prNumber, prDetails, agentType, reviewText, decision) {
  const [owner, repoName] = repo.split('/');
  const agent = AGENT_PROMPTS[agentType];

  // Parse inline comments from review text
  const inlineComments = parseInlineComments(reviewText);

  // Extract summary (without inline comments section)
  const summary = extractSummary(reviewText);

  // Construct review body
  const reviewBody = `## 🤖 **${agent.role} Review**

${summary}

${inlineComments.length > 0 ? `\n**${inlineComments.length} inline comment(s)** posted on specific lines in the "Files changed" tab.\n` : ''}

---

*Automated review by ${agent.role} | Agent expertise: ${agent.focus}*
`;

  console.log(`  Summary: ${summary.substring(0, 100)}...`);
  console.log(`  Inline comments: ${inlineComments.length}`);
  console.log(`  Decision: ${decision}`);

  // Get the commit SHA for the review
  const prData = await octokit.rest.pulls.get({
    owner,
    repo: repoName,
    pull_number: prNumber
  });

  const commitId = prData.data.head.sha;

  // Post the review with inline comments
  try {
    await octokit.rest.pulls.createReview({
      owner,
      repo: repoName,
      pull_number: prNumber,
      commit_id: commitId,
      event: decision, // 'APPROVE', 'REQUEST_CHANGES', or 'COMMENT'
      body: reviewBody,
      comments: inlineComments.map(comment => ({
        path: comment.path,
        line: comment.line,
        body: `**🤖 ${agent.role}**\n\n${comment.body}`
      }))
    });

    console.log(`✅ Posted review as ${agent.role} with ${inlineComments.length} inline comments`);
  } catch (error) {
    console.error(`Error posting review: ${error.message}`);

    // Fallback: Post as regular comment if review API fails
    console.log('Falling back to regular comment...');

    const fallbackComment = `## 🤖 **${agent.role} Review**

${reviewText}

---

*Automated review by ${agent.role} | Agent expertise: ${agent.focus}*

⚠️ Note: Inline comments could not be posted. Issues are listed above.
`;

    await octokit.rest.issues.createComment({
      owner,
      repo: repoName,
      issue_number: prNumber,
      body: fallbackComment
    });

    console.log(`✅ Posted fallback comment as ${agent.role}`);
  }
}

// Main function
async function main() {
  const args = parseArgs();

  // Validate required arguments
  if (!args.agent || !args['pr-number'] || !args.repo || !args['pr-details-file']) {
    console.error('Missing required arguments');
    console.error('Usage: node automated-review.js --agent <type> --pr-number <num> --repo <owner/repo> --pr-details-file <path>');
    process.exit(1);
  }

  // Validate environment variables
  if (!process.env.LLM_API_KEY) {
    console.error('LLM_API_KEY environment variable is required');
    process.exit(1);
  }

  if (!process.env.GITHUB_TOKEN) {
    console.error('GITHUB_TOKEN environment variable is required');
    process.exit(1);
  }

  const agentType = args.agent;
  const prNumber = parseInt(args['pr-number']);
  const repo = args.repo;
  const prDetailsFile = args['pr-details-file'];
  const isRework = args['rework'] === 'true';

  console.log(`\n========================================`);
  console.log(`Automated Peer Review`);
  console.log(`========================================`);
  console.log(`Agent: ${agentType}`);
  console.log(`PR: #${prNumber}`);
  console.log(`Repo: ${repo}`);
  console.log(`Rework review: ${isRework}`);
  console.log(`========================================\n`);

  // Load PR details
  const prDetails = JSON.parse(fs.readFileSync(prDetailsFile, 'utf8'));

  // Initialize Octokit
  const octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN
  });

  // Check for previous review from this agent
  console.log('Checking for previous review from this agent...');
  const previousReview = await getPreviousReview(octokit, repo, prNumber, agentType);

  if (previousReview) {
    console.log(`📋 Found previous review (${previousReview.state}) with ${previousReview.comments.length} comments`);
    console.log('🔄 Entering RE-REVIEW MODE');
  } else {
    console.log('✨ First-time review for this agent');
  }

  // Call LLM API for review
  const reviewText = await callLLMForReview(agentType, prDetails, previousReview, isRework);

  // Parse decision
  const decision = parseReviewDecision(reviewText);

  console.log(`Decision: ${decision}`);

  // Resolve threads if this is a re-review and issues were addressed
  if (previousReview && decision === 'APPROVE') {
    console.log('Resolving previous review threads...');
    await resolveReviewThreads(octokit, repo, prNumber, reviewText, previousReview, isRework);
  }

  // Post review with inline comments
  await postPullRequestReview(octokit, repo, prNumber, prDetails, agentType, reviewText, decision);

  console.log(`\n✅ Review complete!`);
}

// Run main function
main().catch(error => {
  console.error('Error:', error);
  process.exit(1);
});
