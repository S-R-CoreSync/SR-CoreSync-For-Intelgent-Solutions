/*
 * S&R CoreSync For Intelligent Solutions - Sovereign International Arbitration Hub (Mission 104)
 * PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY
 * Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
 * Unauthorized copying, decompilation, redistribution, or external model training is prohibited.
 *
 * Mission 107 wiring: every sealed draft award now issues a sealed execution
 * directive through SRCaseBridge, so the escrow vault of the same case freezes
 * or releases without a second data entry, and the forensics portal can attach
 * its chain-of-custody seals to the same case record.
 */
(function () {
    'use strict';

    var core = window.SRMission;
    var bridge = window.SRCaseBridge;

    var CASE_TYPES = {
        supply: {
            seat: 'Amsterdam (NAI)',
            rules: 'NAI Arbitration Rules 2024',
            law: 'Dutch Civil Code Book 7 + CISG 1980'
        },
        construction: {
            seat: 'Dubai (DIFC-AI)',
            rules: 'DIAC Rules 2022 + FIDIC Red Book 2017',
            law: 'DIFC Law No. 1 of 2008'
        },
        ip: {
            seat: 'Singapore (SIAC)',
            rules: 'SIAC Rules 2025',
            law: 'TRIPS + Singapore IPA'
        },
        finance: {
            seat: 'Riyadh (SCCA)',
            rules: 'SCCA Rules 2023 + AAOIFI Sharia Std. No. 32',
            law: 'Saudi Arbitration Law (Royal Decree M/34)'
        }
    };

    var CASE_TYPE_LABEL = {
        supply: 'توريد',
        construction: 'مقاولات FIDIC',
        ip: 'ملكية فكرية',
        finance: 'تمويل وصكوك'
    };

    var docket = [
        {
            id: 'ARB-2026-0418',
            claimant: 'Rotterdam Logistics B.V.',
            respondent: 'Gulf Trade Holding LLC',
            amount: 1850000,
            type: 'supply',
            docs: 412,
            merit: 0.78
        },
        {
            id: 'ARB-2026-0421',
            claimant: 'Al-Noor Construction Co.',
            respondent: 'Emirates Towers Dev. PJSC',
            amount: 6420000,
            type: 'construction',
            docs: 1290,
            merit: 0.64
        },
        {
            id: 'ARB-2026-0433',
            claimant: 'S&R CoreSync IP Licensing',
            respondent: 'Pacific SoftWorks Pte. Ltd.',
            amount: 940000,
            type: 'ip',
            docs: 238,
            merit: 0.86
        },
        {
            id: 'ARB-2026-0447',
            claimant: 'Damascus Trade Finance House',
            respondent: 'Levant Sukuk Issuer SPV',
            amount: 3175000,
            type: 'finance',
            docs: 655,
            merit: 0.71
        }
    ];

    var selectedCase = docket[0];
    var awardCount = 0;
    var lastAward = null;

    var listEl = document.getElementById('case-list');
    var terminalEl = document.getElementById('arb-terminal');
    var bridgeTerminalEl = document.getElementById('bridge-terminal');

    function typeLabel(type) {
        return CASE_TYPE_LABEL[type] || type;
    }

    function renderDocket() {
        listEl.textContent = '';

        docket.forEach(function (item) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'select-item' + (item.id === selectedCase.id ? ' active' : '');
            btn.setAttribute('aria-pressed', item.id === selectedCase.id ? 'true' : 'false');
            btn.dataset.id = item.id;

            var head = document.createElement('div');
            head.className = 'item-head';

            var name = document.createElement('span');
            name.className = 'item-name';
            name.textContent = item.claimant + '  ⟷  ' + item.respondent;

            var tag = document.createElement('span');
            tag.className = 'item-tag mono';
            tag.textContent = item.id;

            head.appendChild(name);
            head.appendChild(tag);

            var meta = document.createElement('p');
            meta.className = 'item-sub';
            meta.textContent = typeLabel(item.type) +
                ' • ' + core.money(item.amount, 'EUR') +
                ' • المقعد المقترح: ' + CASE_TYPES[item.type].seat +
                ' • ' + item.docs.toLocaleString('en-US') + ' مستند';

            btn.appendChild(head);
            btn.appendChild(meta);

            btn.addEventListener('click', function () {
                selectedCase = item;
                renderDocket();
                renderTerminalWelcome();
                renderBridgePanel();
            });

            listEl.appendChild(btn);
        });

        var totalValue = docket.reduce(function (sum, item) { return sum + item.amount; }, 0);
        var totalDocs = docket.reduce(function (sum, item) { return sum + item.docs; }, 0);

        core.setText('stat-active', String(docket.length));
        core.setText('stat-value', core.money(totalValue, 'EUR'));
        core.setText('kpi-docs', totalDocs.toLocaleString('en-US'));
        core.setText('active-case-badge', selectedCase.id);
    }

    function renderTerminalWelcome() {
        var meta = CASE_TYPES[selectedCase.type];
        core.renderLog(terminalEl, [
            ['log-gold', '[DOCKET] Case ' + selectedCase.id + ' loaded • ' + typeLabel(selectedCase.type)],
            ['log-blue', '[PARTIES] ' + selectedCase.claimant + ' v. ' + selectedCase.respondent],
            ['log-blue', '[SEAT] ' + meta.seat + ' • Rules: ' + meta.rules],
            ['', '[EVIDENCE] ' + selectedCase.docs.toLocaleString('en-US') + ' documents indexed in WORM chain-of-custody vault'],
            ['', '------------------------------------------------------------------'],
            ['log-green', 'Ready. Press "تحليل القضية" to generate the AI-assisted draft award.']
        ]);
    }

    /* ------------------------------------------------------------------
     * Mission 107 execution path panel
     * ------------------------------------------------------------------ */
    function renderBridgePanel() {
        if (!bridge) { return; }

        var summary = bridge.summary(selectedCase.id);

        core.setText('exec-case-badge', selectedCase.id);
        core.setText('bridge-escrow-status', summary.escrowStatusLabel);
        core.setText('bridge-evidence-count',
            summary.evidenceCount === 0
                ? '0'
                : summary.evidenceSealed + ' / ' + summary.evidenceCount + ' مختوم');
        core.setText('bridge-directive',
            summary.directive
                ? bridge.directiveLabel(summary.directive.action) + ' • ' + core.money(summary.directive.amountEUR, 'EUR')
                : 'لم يصدر بعد');
        core.setText('bridge-directive-seal',
            summary.directive ? summary.directive.seal.slice(0, 24) + '…' : '—');

        var escrowLink = document.getElementById('link-open-escrow');
        var forensicLink = document.getElementById('link-open-forensics');
        if (escrowLink) { escrowLink.href = bridge.urlFor('smart-escrow-milestone.html', selectedCase.id); }
        if (forensicLink) { forensicLink.href = bridge.urlFor('digital-forensics-litigation-hub.html', selectedCase.id); }

        var lines = [
            ['log-gold', '[CASE BUS] ' + selectedCase.id + ' • shared record opened for the three portals'],
            ['log-blue', '[EVIDENCE PORTAL] ' + (summary.evidenceCount === 0
                ? 'no sealed evidence attached yet — open the forensics portal and verify an item'
                : summary.evidenceSealed + ' of ' + summary.evidenceCount + ' item(s) carry an ISO/IEC 27037 custody seal')],
            ['log-blue', '[ESCROW PORTAL] ' + summary.escrowStatusLabel]
        ];

        if (summary.directive) {
            lines.push(['log-violet', '[DIRECTIVE] ' + bridge.directiveLabel(summary.directive.action) +
                ' • ' + core.money(summary.directive.amountEUR, 'EUR') +
                ' • issued ' + summary.directive.issuedAt]);
            lines.push(['', '[DIRECTIVE SEAL] ' + summary.directive.seal]);
            lines.push(['log-green', '[AUTO-APPLY] the escrow vault of this case applies the directive on open' +
                (summary.directive.appliedSeal ? ' — applied' : ' — pending')]);
        } else {
            lines.push(['', 'Generate a draft award to issue the execution directive automatically.']);
        }

        lines.push(['', '------------------------------------------------------------------']);
        lines.push(['log-red', 'Interface-level simulation only: no real funds move, and a draft award binds no party before tribunal signature.']);

        core.renderLog(bridgeTerminalEl, lines);
    }

    function logBridge(lines) {
        core.renderLog(bridgeTerminalEl, lines);
    }

    /* ------------------------------------------------------------------
     * Draft award
     * ------------------------------------------------------------------ */
    document.getElementById('btn-analyze').addEventListener('click', function () {
        var meta = CASE_TYPES[selectedCase.type];
        var meritPct = Math.round(selectedCase.merit * 100);
        var recommendedAward = 1000 * Math.round(selectedCase.amount * selectedCase.merit / 1000);
        var costs = Math.round(0.035 * selectedCase.amount);

        var award = {
            platform: 'S&R CoreSync Sovereign International Arbitration Hub',
            mission: 104,
            caseId: selectedCase.id,
            claimant: selectedCase.claimant,
            respondent: selectedCase.respondent,
            disputeType: selectedCase.type,
            seat: meta.seat,
            rules: meta.rules,
            governingLaw: meta.law,
            claimAmountEUR: selectedCase.amount,
            evidenceDocuments: selectedCase.docs,
            claimMeritAssessment: meritPct + '%',
            recommendedAwardEUR: recommendedAward,
            arbitrationCostsEUR: costs,
            enforceability: 'New York Convention 1958 - Art. V compliant',
            disclaimer: 'AI-assisted draft for tribunal review only; not a binding award until signed by the arbitral tribunal.',
            issuedAt: new Date().toISOString(),
            nonce: core.randomHex(12)
        };

        core.sha256Hex(JSON.stringify(award)).then(function (seal) {
            award.sealSHA256 = seal;
            lastAward = award;
            awardCount += 1;

            core.setText('kpi-awards', String(awardCount));
            core.setText('stat-last-seal', seal.slice(0, 16) + '…');

            core.renderLog(terminalEl, [
                ['log-gold', '[TRIBUNAL AI] Analysing ' + selectedCase.id + ' under ' + meta.rules + ' ...'],
                ['log-blue', '[LAW] Governing law resolved: ' + meta.law],
                ['log-blue', '[EVIDENCE] Contract clauses, invoices & correspondence cross-referenced (' + selectedCase.docs + ' docs)'],
                ['log-violet', '[MERITS] Claim merit assessment: ' + meritPct + '% • Recommended award: ' + core.money(recommendedAward, 'EUR')],
                ['log-violet', '[COSTS] Estimated arbitration costs: ' + core.money(costs, 'EUR') + ' (allocated per Art. 42 principle)'],
                ['log-green', '[DRAFT AWARD] Sealed & logged • Enforceable in 172 New York Convention states'],
                ['', '------------------------------------------------------------------'],
                ['', 'SHA-256 Seal: ' + seal],
                ['log-red', 'Advisory draft — final award requires signature of the human arbitral tribunal.']
            ]);

            if (!bridge) { return; }

            return bridge.publishAward({
                caseId: selectedCase.id,
                claimant: selectedCase.claimant,
                respondent: selectedCase.respondent,
                claimAmountEUR: selectedCase.amount,
                disputeType: selectedCase.type,
                seat: meta.seat,
                rules: meta.rules,
                governingLaw: meta.law,
                awardEUR: recommendedAward,
                meritPct: meritPct,
                awardSeal: seal,
                issuedAt: award.issuedAt
            }).then(function (state) {
                renderBridgePanel();
                logBridge([
                    ['log-gold', '[DIRECTIVE ISSUED AUTOMATICALLY] ' + selectedCase.id],
                    ['log-blue', '[ACTION] ' + bridge.directiveLabel(state.directive.action) +
                        ' • ' + core.money(state.directive.amountEUR, 'EUR') +
                        ' of a ' + core.money(state.claimAmountEUR, 'EUR') + ' claim'],
                    ['log-violet', '[DIRECTIVE SEAL] ' + state.directive.seal],
                    ['', '[ROUTING] smart-escrow-milestone.html?case=' + selectedCase.id],
                    ['log-green', '[NEXT] the escrow vault applies the directive on open — no re-keying, no manual freeze click.'],
                    ['', '------------------------------------------------------------------'],
                    ['log-red', 'Draft-award directive: applies to the interface state only and never authorises a real transfer.']
                ]);
            });
        }).catch(function (error) {
            core.renderLog(terminalEl, [
                ['log-red', '[ERROR] Could not seal the draft award: ' + (error && error.message ? error.message : 'unknown error')]
            ]);
        });
    });

    document.getElementById('btn-issue-directive').addEventListener('click', function () {
        if (!bridge) {
            logBridge([['log-red', '[BRIDGE] js/sovereign-case-bridge.js is not loaded on this page.']]);
            return;
        }
        if (!lastAward || lastAward.caseId !== selectedCase.id) {
            logBridge([
                ['log-red', '[DIRECTIVE] No sealed draft award exists for ' + selectedCase.id + ' in this session.'],
                ['', 'Run "تحليل القضية وإصدار مسودة الحكم" first, then re-issue the directive if the analysis changes.']
            ]);
            return;
        }

        var meta = CASE_TYPES[selectedCase.type];
        bridge.publishAward({
            caseId: selectedCase.id,
            claimant: selectedCase.claimant,
            respondent: selectedCase.respondent,
            claimAmountEUR: selectedCase.amount,
            disputeType: selectedCase.type,
            seat: meta.seat,
            rules: meta.rules,
            governingLaw: meta.law,
            awardEUR: lastAward.recommendedAwardEUR,
            meritPct: parseInt(lastAward.claimMeritAssessment, 10) || 0,
            awardSeal: lastAward.sealSHA256,
            issuedAt: lastAward.issuedAt
        }).then(function (state) {
            renderBridgePanel();
            logBridge([
                ['log-gold', '[DIRECTIVE RE-ISSUED] ' + selectedCase.id],
                ['log-blue', '[ACTION] ' + bridge.directiveLabel(state.directive.action) + ' • ' + core.money(state.directive.amountEUR, 'EUR')],
                ['log-violet', '[DIRECTIVE SEAL] ' + state.directive.seal],
                ['log-green', '[ROUTING] open the escrow portal for this case to apply it.']
            ]);
        });
    });

    document.getElementById('btn-export-award').addEventListener('click', function () {
        if (lastAward && lastAward.caseId === selectedCase.id) {
            core.downloadJSON('SR-CoreSync-Arbitration-Award-' + selectedCase.id + '.json', lastAward);
        } else {
            core.renderLog(terminalEl, [
                ['log-red', '[EXPORT] Generate the draft award for ' + selectedCase.id + ' first.']
            ]);
        }
    });

    document.getElementById('new-case-form').addEventListener('submit', function (event) {
        event.preventDefault();

        var claimant = document.getElementById('f-claimant').value.trim();
        var respondent = document.getElementById('f-respondent').value.trim();
        var amount = parseFloat(document.getElementById('f-amount').value);
        var type = document.getElementById('f-type').value;
        var messageEl = document.getElementById('form-msg');

        if (!(claimant && respondent && amount >= 1000)) {
            messageEl.textContent = '  ⚠️ يرجى إدخال أسماء الأطراف وقيمة مطالبة لا تقل عن €1,000';
            messageEl.style.color = '#fda4af';
            return;
        }

        var serial = 448 + docket.length;
        var created = {
            id: 'ARB-2026-0' + serial,
            claimant: claimant,
            respondent: respondent,
            amount: amount,
            type: type,
            docs: 0,
            merit: 0.5 + (serial % 40) / 100
        };

        docket.push(created);
        selectedCase = created;

        renderDocket();
        renderTerminalWelcome();
        renderBridgePanel();

        messageEl.textContent = '  ✅ تم إيداع الطلب ' + created.id;
        messageEl.style.color = '#6ee7b7';
        event.target.reset();
    });

    renderDocket();
    renderTerminalWelcome();
    renderBridgePanel();

    if (bridge) {
        bridge.subscribe(function (caseId) {
            if (caseId === selectedCase.id) { renderBridgePanel(); }
        });
    }
})();
