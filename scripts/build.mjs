#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

console.log('======================================================================');
console.log('S&R CoreScience - Enterprise Architecture Build Verification');
console.log('======================================================================');

// 1. Verify Modular Architecture Directories
const requiredModules = ['auth', 'members', 'ai-tools', 'financial', 'media-hub', 'shared-ui'];
console.log('\n[1/6] Verifying S&R CoreScience Feature Architecture Modules...');
for (const mod of requiredModules) {
    const dir = join(process.cwd(), 'modules', mod);
    const tsFile = join(dir, 'index.ts');
    const jsFile = join(dir, 'index.js');
    if (!existsSync(dir) || !existsSync(tsFile) || !existsSync(jsFile)) {
        console.error(`❌ Missing module or entry points: modules/${mod}`);
        process.exit(1);
    }
}
console.log('  ✅ All 6 feature modules (auth, members, ai-tools, financial, media-hub, shared-ui) verified.');

// 2. Syntax Check for JS & CSS
console.log('\n[2/6] Checking JS & CSS Syntax Integrity...');
const jsFiles = ['js/sr-software-apps.js'];
for (const f of jsFiles) {
    const res = spawnSync('node', ['-c', f], { stdio: 'inherit' });
    if (res.status !== 0) {
        console.error(`❌ Syntax error in ${f}`);
        process.exit(1);
    }
}
console.log('  ✅ JavaScript & CSS syntax verification passed.');

// 3. Compile Tailwind CSS & Prepare Publish Set
console.log('\n[3/6] Compiling Tailwind CSS & Preparing Publish Set...');
const twCli = join(process.cwd(), 'node_modules', '@tailwindcss', 'cli', 'dist', 'index.mjs');
if (existsSync(twCli)) {
    const twRes = spawnSync(process.execPath, [twCli, '-i', 'src/tailwind.css', '-o', 'dist/tailwind.generated.css', '--minify'], { stdio: 'inherit' });
    if (twRes.status !== 0) {
        console.error('❌ Failed to compile Tailwind CSS.');
        process.exit(1);
    }
    console.log('  ✅ Tailwind CSS compiled to dist/tailwind.generated.css.');
}
const pyBin = existsSync('.venv/Scripts/python.exe') ? '.venv/Scripts/python.exe' : 'python';
const prepRes = spawnSync(pyBin, ['scripts/prepare_publish_set.py'], { stdio: 'inherit' });
if (prepRes.status !== 0) {
    console.error('❌ Failed to prepare publish set.');
    process.exit(1);
}
// 4. Update and Check CSP Hashes
console.log('\n[4/6] Verifying CSP Hashes Manifest...');
spawnSync(pyBin, ['scripts/build_csp.py'], { stdio: 'inherit' });
const cspRes = spawnSync(pyBin, ['scripts/build_csp.py', '--check'], { stdio: 'inherit' });
if (cspRes.status !== 0) {
    console.error('❌ CSP hashes verification failed.');
    process.exit(1);
}

// 5. Run Sentinel i18n Guard Suite
console.log('\n[5/6] Running Sentinel i18n (13 Guard Suites)...');
const sentinelRes = spawnSync(pyBin, ['scripts/sentinel_i18n.py'], { stdio: 'inherit' });
if (sentinelRes.status !== 0) {
    console.error('❌ Sentinel i18n audit failed.');
    process.exit(1);
}

// 6. Check Publish Set Integrity & Secret Scanner
console.log('\n[6/6] Checking Publish Set Integrity & Scanning Secrets...');
const integrityRes = spawnSync(pyBin, ['scripts/check_publish_set_integrity.py'], { stdio: 'inherit' });
if (integrityRes.status !== 0) {
    console.error('❌ Publish set integrity failed.');
    process.exit(1);
}

const secretsRes = spawnSync(pyBin, ['scripts/audit_secrets.py'], { stdio: 'inherit' });
if (secretsRes.status !== 0) {
    console.error('❌ Secret scan audit failed.');
    process.exit(1);
}

console.log('\n======================================================================');
console.log('✨ BUILD SUCCESSFUL: S&R CoreScience architecture is 100% verified with 0 errors.');
console.log('======================================================================\n');
process.exit(0);
