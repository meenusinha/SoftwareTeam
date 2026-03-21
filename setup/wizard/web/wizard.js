/**
 * Setup Wizard - Client-side logic
 *
 * Manages screen navigation, API calls to the Python backend,
 * and UI updates for the setup wizard.
 */

const state = {
  currentScreen: 0,
  totalScreens: 10,
  workflowMode: null,      // 'github' or 'local'
  osInfo: null,
  projectPath: null,
  selectedTool: null,
  selectedProvider: null,
};

// --- API helpers ---

async function api(path, body) {
  const opts = { headers: { 'Content-Type': 'application/json' } };
  if (body !== undefined) {
    opts.method = 'POST';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  return res.json();
}

async function apiWithTimeout(path, body, timeoutSecs) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutSecs * 1000);
  try {
    const opts = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    };
    const res = await fetch(path, opts);
    return res.json();
  } catch (e) {
    return { success: false, message: 'Request timed out — the installer may still be running in the background. Please wait a moment and try again.', error_log: e.message };
  } finally {
    clearTimeout(id);
  }
}

// --- Screen navigation ---

function showScreen(index) {
  document.querySelectorAll('.screen').forEach((el, i) => {
    el.classList.toggle('active', i === index);
  });
  state.currentScreen = index;
  updateProgress();
}

function nextScreen() {
  let next = state.currentScreen + 1;

  // Skip logic based on workflow mode
  if (state.workflowMode === 'local') {
    // Skip screens not needed for local mode:
    // 2 (prerequisites - git/gh), 3 (GitHub account), 4 (token), 6 (LLM)
    const skipScreens = [2, 3, 4, 6];
    while (skipScreens.includes(next) && next < state.totalScreens) {
      next++;
    }
  }

  if (next < state.totalScreens) {
    showScreen(next);
    initScreen(next);
  }
}

function prevScreen() {
  let prev = state.currentScreen - 1;

  if (state.workflowMode === 'local') {
    const skipScreens = [2, 3, 4, 6];
    while (skipScreens.includes(prev) && prev > 0) {
      prev--;
    }
  }

  if (prev >= 0) {
    showScreen(prev);
  }
}

function updateProgress() {
  const skipScreens = state.workflowMode === 'local' ? [2, 3, 4, 6] : [];
  document.querySelectorAll('.progress-step').forEach((el, i) => {
    el.classList.remove('active', 'completed', 'skipped');
    if (skipScreens.includes(i)) {
      el.classList.add('skipped');
    } else if (i < state.currentScreen) {
      el.classList.add('completed');
    } else if (i === state.currentScreen) {
      el.classList.add('active');
    }
  });

  // Update step label
  const label = document.getElementById('progress-label');
  if (label) {
    const totalSteps = state.totalScreens - skipScreens.length;
    const activeSteps = Array.from({ length: state.currentScreen + 1 }, (_, i) => i)
      .filter(i => !skipScreens.includes(i)).length;
    label.textContent = `Step ${activeSteps} of ${totalSteps}`;
  }
}

// --- Screen initializers ---

async function initScreen(index) {
  switch (index) {
    case 0: await initWelcome(); break;
    case 2: await initPrerequisites(); break;
    case 3: await initGitHubAccount(); break;
    case 4: await initToken(); break;
    case 5: await initForkClone(); break;
    case 7: await initToolSelect(); break;
    case 9: initDone(); break;
  }
}

// Screen 9: Done
function initDone() {
  // GitHub Actions note moved to verification screen (Issue 9)
}

// Screen 0: Welcome
async function initWelcome() {
  const info = await api('/api/os-info');
  state.osInfo = info;
  state.userCwd = info.user_cwd || '';
  document.getElementById('os-display').textContent = info.display_name || 'Unknown OS';
}

// Screen 2: Prerequisites
async function initPrerequisites() {
  await refreshPrerequisites();
}

async function refreshPrerequisites() {
  const status = await api('/api/prerequisites/status');

  updateStatusItem('git-status', status.git);
  updateStatusItem('gh-status', status.gh);

  const allInstalled = status.git.installed && status.gh.installed;
  const nextBtn = document.getElementById('prereq-next');
  if (nextBtn) nextBtn.disabled = !allInstalled;

  // Update description based on actual status
  const desc = document.getElementById('prereq-description');
  if (desc) {
    if (allInstalled) {
      desc.textContent = 'All prerequisites are ready!';
    } else if (!status.git.installed && !status.gh.installed) {
      desc.textContent = "We'll automatically install the tools you need.";
    } else {
      desc.textContent = "Almost there — installing the remaining tool.";
    }
  }
}

function updateStatusItem(id, info) {
  const el = document.getElementById(id);
  if (!el) return;
  const icon = el.querySelector('.status-icon');
  const version = el.querySelector('.version');
  const actionBtn = el.querySelector('.action-btn');

  if (info.installed) {
    icon.textContent = '\u2705';
    version.textContent = info.version || 'Installed';
    if (actionBtn) actionBtn.style.display = 'none';
  } else {
    icon.textContent = '\u274c';
    version.textContent = 'Not installed';
    if (actionBtn) actionBtn.style.display = '';
  }
}

// --- Install job polling ---

let _pollTimer = null;
let _logOffset = 0;

function _startLogBox(boxId, contentId) {
  const box = document.getElementById(boxId);
  const content = document.getElementById(contentId);
  if (box) box.style.display = '';
  if (content) content.textContent = '';
  _logOffset = 0;
}

function toggleLogBox(boxId, contentId) {
  const box = document.getElementById(boxId);
  if (!box) return;
  const content = document.getElementById(contentId);
  const btn = box.querySelector('.log-toggle-btn');
  const isHidden = content && content.style.display === 'none';
  if (content) content.style.display = isHidden ? '' : 'none';
  if (btn) btn.textContent = isHidden ? 'Hide' : 'Show';
}

function _pollInstallLog(jobId, contentId, onDone) {
  if (_pollTimer) clearInterval(_pollTimer);
  _pollTimer = setInterval(async () => {
    const res = await api(`/api/install/log?job_id=${jobId}`);
    if (!res || res.error) { clearInterval(_pollTimer); return; }

    // Append only new lines
    const newLines = res.lines.slice(_logOffset);
    _logOffset = res.lines.length;
    if (newLines.length > 0) {
      const content = document.getElementById(contentId);
      if (content) {
        content.textContent += newLines.join('\n') + '\n';
        content.scrollTop = content.scrollHeight;
      }
    }

    if (res.done) {
      clearInterval(_pollTimer);
      _pollTimer = null;
      onDone(res);
    }
  }, 500);
}

async function installPrerequisite(tool) {
  const btn = event.target;
  const origText = btn.textContent;
  btn.disabled = true;

  _startLogBox('prereq-log-box', 'prereq-log-content');
  showAlert('prereq-alerts', '', 'info');

  let elapsed = 0;
  const timer = setInterval(() => {
    elapsed++;
    btn.textContent = `Installing... (${elapsed}s)`;
  }, 1000);
  btn.textContent = 'Installing...';

  const startRes = await api('/api/install/start', { kind: 'prerequisite', tool });
  if (!startRes.job_id) {
    clearInterval(timer);
    showAlert('prereq-alerts', startRes.message || 'Failed to start installation.', 'danger');
    btn.textContent = origText;
    btn.disabled = false;
    return;
  }

  _pollInstallLog(startRes.job_id, 'prereq-log-content', async (result) => {
    clearInterval(timer);
    if (result.success) {
      await refreshPrerequisites();
      showAlert('prereq-alerts', `${tool === 'git' ? 'Git' : 'GitHub CLI'} installed successfully!`, 'success');
      btn.textContent = '\u2713 Installed';
    } else {
      showAlert('prereq-alerts', result.message || 'Installation failed. See log above.', 'danger');
      btn.textContent = origText;
      btn.disabled = false;
    }
  });
}

// Screen 3: GitHub Account
async function initGitHubAccount() {
  const status = await api('/api/github/auth-status');
  const el = document.getElementById('gh-auth-info');
  const loginActions = document.getElementById('gh-login-actions');
  const instructions = document.getElementById('gh-login-instructions');

  if (status.authenticated) {
    el.innerHTML = `
      <div class="alert alert-success">
        Signed in as <strong>${status.username || 'GitHub user'}</strong>
      </div>`;
    document.getElementById('gh-account-next').disabled = false;
    if (loginActions) loginActions.style.display = 'none';
    // Issue 2: Hide instructions when authenticated
    if (instructions) instructions.style.display = 'none';
  } else {
    el.innerHTML = `
      <div class="alert alert-warning">Not signed in to GitHub</div>`;
    document.getElementById('gh-account-next').disabled = true;
    if (loginActions) loginActions.style.display = '';
    // Issue 2: Show instructions when NOT authenticated
    if (instructions) instructions.style.display = '';
  }
}

async function githubLogin() {
  const btn = event.target;
  btn.textContent = 'Starting sign-in...';
  btn.disabled = true;

  const result = await api('/api/github/login', {});

  if (result.success && result.device_code) {
    // Show device code and link in the UI
    const url = result.verification_url || 'https://github.com/login/device';
    showAlert('gh-account-alerts', `
      <div style="text-align:center; padding:10px 0;">
        <p style="margin-bottom:12px;">Open this URL and enter the code below:</p>
        <p><a href="${url}" target="_blank" style="color:#2563eb; font-size:1.1em;">${url}</a></p>
        <p style="font-size:2em; font-weight:bold; letter-spacing:6px; margin:16px 0; font-family:monospace; user-select:all;">${result.device_code}</p>
        <p style="color:#666;">After you authorize, click <strong>Check Status</strong> below.</p>
      </div>`, 'info');
    btn.textContent = 'Check Status';
    btn.disabled = false;
    // Change button behavior to poll
    btn.onclick = async function() {
      btn.textContent = 'Checking...';
      btn.disabled = true;
      // Poll the login endpoint (returns status) and re-check auth
      await api('/api/github/login', {});
      await initGitHubAccount();
      // If still not authenticated, restore button
      const status = await api('/api/github/auth-status');
      if (!status.authenticated) {
        btn.textContent = 'Check Status';
        btn.disabled = false;
      }
    };
  } else if (result.success && result.status === 'complete') {
    showAlert('gh-account-alerts', 'Successfully signed in!', 'success');
    await initGitHubAccount();
    btn.textContent = 'Sign In with Browser';
    btn.disabled = false;
    btn.onclick = githubLogin;
  } else {
    showAlert('gh-account-alerts', result.message || 'Login failed. Try using a token instead (next screen).', 'warning');
    btn.textContent = 'Sign In with Browser';
    btn.disabled = false;
    btn.onclick = githubLogin;
  }
}

// Screen 4: GitHub Token
async function initToken() {
  const status = await api('/api/github/auth-status');
  if (status.authenticated) {
    // Issue 3: Remove duplicate alert - description is already shown on the page
    // Already signed in via browser — gh CLI auth is sufficient for PR creation
    const container = document.getElementById('token-alerts');
    if (container) container.innerHTML = '';
    document.getElementById('token-next').disabled = false;
  }
}

async function saveGitHubToken() {
  const input = document.getElementById('github-token-input');
  const token = input.value.trim();
  if (!token) {
    showAlert('token-alerts', 'Please paste your GitHub token.', 'warning');
    return;
  }

  const btn = document.getElementById('save-token-btn');
  btn.textContent = 'Saving...';
  btn.disabled = true;

  const result = await api('/api/github/token', { token });

  if (result.success) {
    showAlert('token-alerts', 'Token saved and authenticated!', 'success');
    document.getElementById('token-next').disabled = false;
    btn.textContent = '✓ Saved';
  } else {
    showAlert('token-alerts', result.message, 'danger');
    btn.textContent = 'Save Token';
    btn.disabled = false;
  }
}

// Screen 5: Fork & Clone / Local Copy
async function initForkClone() {
  // Default to the directory where the user ran the curl command
  const defaultPath = state.userCwd || '';
  if (defaultPath) {
    state.projectPath = defaultPath;
    // Pre-fill both path inputs (github and local)
    const ghInput = document.getElementById('custom-path-input');
    const localInput = document.getElementById('local-custom-path');
    if (ghInput) ghInput.value = defaultPath;
    if (localInput) localInput.value = defaultPath;
  }
}

function useCustomPath() {
  const input = document.getElementById('custom-path-input') || document.getElementById('local-custom-path');
  if (input && input.value.trim()) {
    state.projectPath = input.value.trim();
  }
}

async function browsePath(targetInputId) {
  const result = await api('/api/paths/browse');
  if (result.success && result.path) {
    state.projectPath = result.path;
    const input = document.getElementById(targetInputId);
    if (input) input.value = result.path;
  } else if (result.message) {
    showAlert('clone-alerts', result.message, 'warning');
    showAlert('local-alerts', result.message, 'warning');
  }
}

async function forkAndClone() {
  const btn = document.getElementById('fork-clone-btn');
  const projectName = document.getElementById('project-name-input').value.trim() || 'SoftwareTeam';
  // Issue 6: Add spinner while forking/cloning
  btn.innerHTML = '<span class="spinner"></span> Forking & Cloning...';
  btn.disabled = true;

  const result = await api('/api/github/fork-clone', {
    path: state.projectPath,
    project_name: projectName,
  });

  if (result.success) {
    state.projectPath = result.project_path;
    showAlert('clone-alerts', `${result.message}<br><small style="color:var(--text-muted)">Repository context configured for PR creation.</small>`, 'success');
    document.getElementById('clone-next').disabled = false;
    btn.textContent = '✓ Forked & Cloned';
  } else {
    showAlert('clone-alerts', result.message, 'danger');
    btn.textContent = 'Fork & Clone';
    btn.disabled = false;
  }
}

// Screen 5 (local): Copy files
async function copyLocal() {
  const btn = document.getElementById('local-copy-btn');
  const projectName = document.getElementById('local-project-name').value.trim() || 'SoftwareTeam';
  // Issue 6: Add spinner while copying
  btn.innerHTML = '<span class="spinner"></span> Copying files...';
  btn.disabled = true;

  const result = await api('/api/local/copy', {
    path: state.projectPath,
    project_name: projectName,
  });

  if (result.success) {
    state.projectPath = result.project_path;
    showAlert('local-alerts', result.message, 'success');
    document.getElementById('local-next').disabled = false;
    btn.textContent = '✓ Copied';
  } else {
    showAlert('local-alerts', result.message, 'danger');
    btn.textContent = 'Copy Project Files';
    btn.disabled = false;
  }
}

// Screen 6: LLM Provider
const PROVIDERS = [
  { id: 'copilot', name: 'GitHub Copilot', needs_key: false,
    note: 'No API key needed. Uses repository authentication.' },
  { id: 'openai', name: 'OpenAI (GPT-4)', cost: '$$',
    url: 'https://platform.openai.com/api-keys',
    steps: ['Go to platform.openai.com/api-keys', 'Sign in or create account', 'Click "Create new secret key"', 'Copy the key (starts with sk-...)'] },
  { id: 'anthropic', name: 'Anthropic (Claude)', cost: '$$$',
    url: 'https://console.anthropic.com/',
    steps: ['Go to console.anthropic.com', 'Sign in or create account', 'Go to "API Keys" section', 'Click "Create Key"', 'Copy the key (starts with sk-ant-...)'] },
  { id: 'gemini', name: 'Google Gemini', cost: '$',
    url: 'https://makersuite.google.com/app/apikey',
    steps: ['Go to makersuite.google.com/app/apikey', 'Sign in with Google account', 'Click "Create API Key"', 'Select or create a project', 'Copy the key'] },
  { id: 'azure', name: 'Azure OpenAI', cost: '$$$', needs_endpoint: true,
    url: 'https://portal.azure.com/',
    steps: ['Go to portal.azure.com', 'Search for "Azure OpenAI"', 'Create a resource', 'Go to "Keys and Endpoint"', 'Copy Key 1 and the Endpoint URL'] },
  { id: 'cohere', name: 'Cohere', cost: '$',
    url: 'https://dashboard.cohere.com/',
    steps: ['Go to dashboard.cohere.com', 'Sign in or create account', 'Go to "API Keys"', 'Copy your Production key'] },
  { id: 'mistral', name: 'Mistral AI', cost: '$',
    url: 'https://console.mistral.ai/',
    steps: ['Go to console.mistral.ai', 'Sign in or create account', 'Go to "API Keys"', 'Click "Create new key"', 'Copy the key'] },
];

function selectProvider(id) {
  state.selectedProvider = id;
  const provider = PROVIDERS.find(p => p.id === id);
  document.querySelectorAll('.radio-option').forEach(el => {
    el.classList.toggle('selected', el.dataset.provider === id);
    const radio = el.querySelector('input[type="radio"]');
    if (radio) radio.checked = (el.dataset.provider === id);
  });

  const detail = document.getElementById('provider-detail');
  if (provider.needs_key === false) {
    detail.innerHTML = `
      <div class="alert alert-info">${provider.note}</div>`;
    document.getElementById('llm-api-key-group').style.display = 'none';
    document.getElementById('azure-endpoint-group').style.display = 'none';
    document.getElementById('llm-next').disabled = false;
  } else {
    let stepsHtml = '<ol>' + provider.steps.map(s => `<li>${s}</li>`).join('') + '</ol>';
    detail.innerHTML = `
      <div class="provider-info">
        <div class="provider-cost">Cost: ${provider.cost}</div>
        <a href="${provider.url}" target="_blank" class="btn btn-outline btn-sm" style="margin-bottom:12px">
          Open ${provider.name} &rarr;
        </a>
        <div class="instructions">${stepsHtml}</div>
      </div>`;
    document.getElementById('llm-api-key-group').style.display = '';
    document.getElementById('azure-endpoint-group').style.display = provider.needs_endpoint ? '' : 'none';
    document.getElementById('llm-next').disabled = true;
  }
}

async function saveLLMConfig() {
  const provider = state.selectedProvider;
  const apiKey = document.getElementById('llm-api-key').value.trim();
  const azureEndpoint = document.getElementById('azure-endpoint')?.value.trim() || '';

  if (!provider) {
    showAlert('llm-alerts', 'Please select a provider.', 'warning');
    return;
  }

  const providerInfo = PROVIDERS.find(p => p.id === provider);
  if (providerInfo.needs_key !== false && !apiKey) {
    showAlert('llm-alerts', 'Please enter your API key.', 'warning');
    return;
  }

  const btn = document.getElementById('save-llm-btn');
  btn.textContent = 'Saving...';
  btn.disabled = true;

  const result = await api('/api/llm/configure', {
    provider, api_key: apiKey, azure_endpoint: azureEndpoint,
  });

  if (result.success) {
    // Check if GitHub secrets had issues (local config succeeded but secrets failed)
    const secretsFailed = result.github_secrets && result.github_secrets.results &&
      result.github_secrets.results.some(s => !s.success);
    if (secretsFailed) {
      const failedNames = result.github_secrets.results.filter(s => !s.success).map(s => s.secret).join(', ');
      showAlert('llm-alerts', `${providerInfo.name} configured locally, but GitHub Actions secrets failed (${failedNames}). Automated peer reviews may not work.`, 'warning');
    } else {
      showAlert('llm-alerts', `${providerInfo.name} configured!`, 'success');
    }
    document.getElementById('llm-next').disabled = false;
    btn.textContent = '✓ Saved';
    // Issue 7: Disable radio buttons after save
    document.querySelectorAll('.radio-option').forEach(el => {
      el.style.pointerEvents = 'none';
      el.style.opacity = '0.6';
    });
  } else {
    showAlert('llm-alerts', result.message, 'danger');
    btn.textContent = 'Save Configuration';
    btn.disabled = false;
  }
}

// GitHub Actions modal
function showActionsModal() {
  const m = document.getElementById('actions-modal');
  if (m) m.style.display = 'flex';
}

function closeActionsModal() {
  const m = document.getElementById('actions-modal');
  if (m) m.style.display = 'none';
}

// Screen 7: AI Tool Selection
async function initToolSelect() {
  if (state.workflowMode === 'github') showActionsModal();
  const data = await api('/api/tools/list');
  const grid = document.getElementById('tool-grid');
  grid.innerHTML = '';

  (data.tools || []).forEach(tool => {
    const card = document.createElement('div');
    card.className = 'tool-card';
    card.dataset.tool = tool.id;
    card.innerHTML = `
      <div class="tool-name">${tool.name}</div>
      <div class="tool-desc">${tool.description}</div>
      <span class="tool-difficulty">${tool.difficulty}</span>`;
    card.onclick = () => selectTool(tool.id);
    grid.appendChild(card);
  });
}

async function selectTool(id) {
  state.selectedTool = id;
  document.querySelectorAll('.tool-card').forEach(el => {
    el.classList.toggle('selected', el.dataset.tool === id);
  });

  // Check if the tool is already installed
  const installBtn = document.getElementById('install-tool-btn');
  const launchBtn = document.getElementById('launch-tool-btn');
  const nextBtn = document.getElementById('tool-next');

  installBtn.disabled = true;
  installBtn.textContent = 'Checking...';
  showAlert('tool-alerts', '', 'info');

  const status = await api('/api/tools/check', { tool: id });

  if (status.installed) {
    showAlert('tool-alerts', `${id} is already installed!`, 'success');
    installBtn.textContent = 'Already Installed';
    installBtn.disabled = true;
    launchBtn.style.display = '';
    nextBtn.disabled = false;
  } else {
    showAlert('tool-alerts', '', 'info');
    installBtn.textContent = 'Install';
    installBtn.disabled = false;
    launchBtn.style.display = 'none';
    nextBtn.disabled = true;
  }
}

async function installTool() {
  if (!state.selectedTool) return;

  const btn = document.getElementById('install-tool-btn');
  btn.disabled = true;

  _startLogBox('tool-log-box', 'tool-log-content');
  showAlert('tool-alerts', '', 'info');

  let elapsed = 0;
  const timer = setInterval(() => {
    elapsed++;
    btn.innerHTML = `<span class="spinner"></span> Installing... (${elapsed}s)`;
  }, 1000);
  btn.innerHTML = '<span class="spinner"></span> Installing...';

  const startRes = await api('/api/install/start', { kind: 'tool', tool: state.selectedTool });
  if (!startRes.job_id) {
    clearInterval(timer);
    showAlert('tool-alerts', startRes.message || 'Failed to start installation.', 'danger');
    btn.textContent = 'Retry';
    btn.disabled = false;
    return;
  }

  _pollInstallLog(startRes.job_id, 'tool-log-content', (result) => {
    clearInterval(timer);
    if (result.success) {
      showAlert('tool-alerts', result.message, 'success');
      document.getElementById('launch-tool-btn').style.display = '';
      document.getElementById('tool-next').disabled = false;
      btn.textContent = '\u2713 Installed';
    } else {
      showAlert('tool-alerts', result.message || 'Installation failed. See log above.', 'danger');
      btn.textContent = 'Retry';
      btn.disabled = false;
    }
  });
}

// Animation info per tool: { desc, steps[], note }
const ANIMATION_INFO = {
  'cursor': {
    auto: true,
    steps: [
      'The animation window launches automatically when Cursor opens the project.',
      'Cursor reads <code>.vscode/tasks.json</code> — no extra setup needed.',
      '<strong>⚠️ Workspace Trust required:</strong> When Cursor opens the project for the first time, click <strong>"Yes, I trust the authors"</strong> in the trust dialog — automatic tasks are blocked in Restricted mode and the animation will not launch.',
      'The window shows which agent is active and updates as agents hand off.',
    ],
  },
  'windsurf': {
    auto: true,
    steps: [
      'The animation window launches automatically when Windsurf opens the project.',
      'Windsurf reads <code>.vscode/tasks.json</code> — no extra setup needed.',
      '<strong>⚠️ Workspace Trust required:</strong> When Windsurf opens the project for the first time, click <strong>"Yes, I trust the authors"</strong> in the trust dialog — automatic tasks are blocked in Restricted mode and the animation will not launch.',
      'The window shows which agent is active and updates as agents hand off.',
    ],
  },
  'vscode': {
    auto: true,
    steps: [
      'The animation window launches automatically when VS Code opens the project.',
      '<code>.vscode/settings.json</code> already has <code>task.allowAutomaticTasks: on</code> — no manual approval needed.',
      '<strong>⚠️ Workspace Trust required:</strong> When VS Code opens the project for the first time, click <strong>"Yes, I trust the authors"</strong> in the trust dialog — automatic tasks are blocked in Restricted mode and the animation will not launch.',
      'The window shows which agent is active and updates as agents hand off.',
    ],
  },
  'copilot': {
    auto: true,
    steps: [
      'The animation window launches automatically when VS Code opens the project.',
      '<code>.vscode/settings.json</code> already has <code>task.allowAutomaticTasks: on</code> — no manual approval needed.',
      '<strong>⚠️ Workspace Trust required:</strong> When VS Code opens the project for the first time, click <strong>"Yes, I trust the authors"</strong> in the trust dialog — automatic tasks are blocked in Restricted mode and the animation will not launch.',
      'The window shows which agent is active and updates as agents hand off.',
    ],
  },
  'claude-code': {
    auto: false,
    steps: [
      'Claude Code is a terminal tool — VS Code auto-tasks don\'t apply.',
      'The animation starts automatically when Claude executes <strong>Step 1 (IT Agent)</strong>.',
      'Just give Claude a task in the terminal and the window will appear.',
    ],
    note: 'Make sure Python is available in your terminal for the animation to launch.',
  },
  'aider': {
    auto: false,
    steps: [
      'Aider is a terminal tool — VS Code auto-tasks don\'t apply.',
      'The animation starts automatically when Aider executes <strong>Step 1 (IT Agent)</strong>.',
      'Run <code>aider</code> from the project folder and give it a task.',
    ],
    note: 'Make sure Python is available in your terminal for the animation to launch.',
  },
};

function showAnimationModal() {
  const info = ANIMATION_INFO[state.selectedTool];
  if (!info) { _doLaunchTool(); return; }

  const desc = document.getElementById('animation-modal-desc');
  const stepsEl = document.getElementById('animation-modal-steps');

  if (desc) {
    desc.textContent = info.auto
      ? 'A floating pixel-art window shows which AI agent is active — it launches automatically when you open the project.'
      : 'A floating pixel-art window shows which AI agent is active — it starts when the AI executes its first step.';
  }

  if (stepsEl) {
    const stepsHtml = info.steps.map(s => `
      <div class="modal-step">
        <span class="step-num">&#10003;</span>
        <span>${s}</span>
      </div>`).join('');
    const noteHtml = info.note
      ? `<p style="margin-top:12px; font-size:13px; color:var(--text-muted)">💡 ${info.note}</p>`
      : '';
    stepsEl.innerHTML = stepsHtml + noteHtml;
  }

  const m = document.getElementById('animation-modal');
  if (m) m.style.display = 'flex';
}

function closeAnimationModal(andLaunch) {
  const m = document.getElementById('animation-modal');
  if (m) m.style.display = 'none';
  if (andLaunch) _doLaunchTool();
}

async function launchTool() {
  if (!state.selectedTool || !state.projectPath) {
    showAlert('tool-alerts', 'No project path set. Please go back and set up your project.', 'warning');
    return;
  }
  showAnimationModal();
}

async function _doLaunchTool() {
  const btn = document.getElementById('launch-tool-btn');
  btn.textContent = 'Launching...';
  btn.disabled = true;

  const result = await api('/api/tools/launch', {
    tool: state.selectedTool,
    project_path: state.projectPath,
  });

  if (result.success) {
    showAlert('tool-alerts', result.message, 'success');
    btn.textContent = '✓ Launched';
    btn.disabled = true;
  } else {
    showAlert('tool-alerts', result.message, 'danger');
    btn.textContent = 'Launch';
    btn.disabled = false;
  }
}

// Screen 8: Verification
const TOOL_INSTRUCTIONS = {
  'cursor': { file: '.cursorrules', name: 'Cursor' },
  'windsurf': { file: '.windsurfrules', name: 'Windsurf' },
  'claude-code': { file: 'CLAUDE.md', name: 'Claude Code' },
  'vscode': { file: '.continuerules', name: 'VS Code + Continue' },
  'copilot': { file: '.github/copilot-instructions.md', name: 'VS Code + GitHub Copilot' },
  'aider': { file: '.aider.conf.yml', name: 'Aider' },
};

function initVerification() {
  const tool = TOOL_INSTRUCTIONS[state.selectedTool] || { file: 'CLAUDE.md', name: 'your AI tool' };
  document.getElementById('verify-tool-name').textContent = tool.name;
  document.getElementById('verify-instruction-file').textContent = tool.file;

  // Expected first agent depends on workflow mode
  const firstAgent = state.workflowMode === 'local' ? 'Product Owner' : 'IT Agent';
  const firstRole = state.workflowMode === 'local' ? 'Product Owner' : 'IT Agent';

  document.getElementById('verify-expected-agent').textContent = `"${firstAgent}"`;
  document.getElementById('verify-expected-agent-2').textContent = firstAgent;

  const fallbackPrompt = `Please read the file ${tool.file} in the project root and follow the workflow guide defined there. Start as the ${firstRole}.`;
  document.getElementById('fallback-prompt').textContent = fallbackPrompt;

}

// --- Utility functions ---

function showAlert(containerId, message, type) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    const btn = event.target;
    const orig = btn.textContent;
    btn.textContent = 'Copied!';
    setTimeout(() => { btn.textContent = orig; }, 1500);
  });
}

// Screen 1: Workflow mode selection
function selectWorkflow(mode) {
  state.workflowMode = mode;
  document.querySelectorAll('#screen-1 .radio-option').forEach(el => {
    el.classList.toggle('selected', el.dataset.mode === mode);
    const radio = el.querySelector('input[type="radio"]');
    if (radio) radio.checked = (el.dataset.mode === mode);
  });
  document.getElementById('workflow-next').disabled = false;

  // Show/hide local-mode project screen (screen index 5 is reused)
  if (mode === 'local') {
    // We'll show a local copy screen instead of fork/clone
    document.getElementById('fork-clone-section').style.display = 'none';
    document.getElementById('local-copy-section').style.display = '';
  } else {
    document.getElementById('fork-clone-section').style.display = '';
    document.getElementById('local-copy-section').style.display = 'none';
  }
}

// --- Initialization ---

document.addEventListener('DOMContentLoaded', () => {
  showScreen(0);
  initScreen(0);
});
