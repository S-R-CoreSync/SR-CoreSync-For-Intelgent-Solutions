// server.js – Simple Express server with PowerShell runner API
// ---------------------------------------------------------------
// This server serves static files from the project root (index.html, assets, etc.)
// and provides an endpoint `/api/run-ps` that executes a selected PowerShell
// script from the extracted repository. The script name is passed in the
// JSON body { "script": "relative/path/to/file.ps1" }.
// ---------------------------------------------------------------

const express = require('express');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files (index.html, CSS, JS, assets) from the project root
app.use(express.static(path.join(__dirname)));

// API: Run a PowerShell script
app.post('/api/run-ps', (req, res) => {
  const script = req.body.script;
  if (!script) {
    return res.status(400).json({ error: 'Missing "script" in request body' });
  }
  // Resolve the script path inside the extracted PowerShell repo
  const scriptPath = path.resolve(__dirname, 'powershell_repo', script);

  // Simple security check – ensure the path stays within the repo folder
  if (!scriptPath.startsWith(path.resolve(__dirname, 'powershell_repo'))) {
    return res.status(400).json({ error: 'Invalid script path' });
  }

  // Execute PowerShell
  const command = `powershell -NoProfile -ExecutionPolicy Bypass -File "${scriptPath}"`;
  exec(command, { timeout: 15000 }, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: error.message, stderr });
    }
    res.json({ stdout, stderr });
  });
});

// Health check
app.get('/health', (req, res) => res.send('OK'));

app.listen(PORT, () => {
  console.log(`🚀 Server listening on http://localhost:${PORT}`);
});
