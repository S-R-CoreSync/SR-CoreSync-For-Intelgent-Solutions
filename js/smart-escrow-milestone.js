/*
 * S&R CoreSync For Intelligent Solutions - Smart Escrow & Dispute Milestone Engine (Mission 107 - Part 2)
 * PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY
 * Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
 */
(function () {
    'use strict';
    var core = window.SRMission;

    var contractTypes = {
        milestone: { label: "توريد بمراحل إنجاز", std: "ICC Model Commercial Contract 2020", multiSig: "3-of-5" },
        fidic: { label: "إنشاءات FIDIC Red Book", std: "FIDIC Conditions of Contract 2017", multiSig: "4-of-6" },
        merger: { label: "استحواذ واندماج M&A", std: "Delaware / Dutch Civil Code Holdback", multiSig: "3-of-4" },
        sukuk: { label: "صكوك إجارة ومرابحة", std: "AAOIFI Sharia Standard No. 17", multiSig: "3-of-5" }
    };

    var escrowVaults = [
        {
            id: "ESC-2026-101",
            buyer: "Saudi Aramco Logistics",
            seller: "ASML Lithography B.V.",
            totalAmount: 4800000,
            releasedAmount: 1440000, // 30% advance released
            currentStage: 2,
            totalStages: 3,
            stageName: "المرحلة 2: اجتياز اختبارات المعايرة والمصنع (40%)",
            type: "milestone",
            status: "ACTIVE_IN_PROGRESS",
            linkedArbitration: "ARB-2026-0418"
        },
        {
            id: "ESC-2026-102",
            buyer: "Emirates Towers Dev. PJSC",
            seller: "Al-Noor Construction Co.",
            totalAmount: 12500000,
            releasedAmount: 6250000, // 50%
            currentStage: 3,
            totalStages: 4,
            stageName: "المرحلة 3: أعمال الخرسانة والهيكل الإنشائي (25%)",
            type: "fidic",
            status: "DISPUTED_FROZEN", // Currently under arbitration!
            linkedArbitration: "ARB-2026-0421"
        },
        {
            id: "ESC-2026-103",
            buyer: "S&R Sovereign Capital Fund",
            seller: "Pacific SoftWorks Pte. Ltd.",
            totalAmount: 1850000,
            releasedAmount: 0,
            currentStage: 1,
            totalStages: 3,
            stageName: "المرحلة 1: تدقيق الكود المصدري ونقل الملكية الفكرية (35%)",
            type: "merger",
            status: "ACTIVE_IN_PROGRESS",
            linkedArbitration: "ARB-2026-0433"
        },
        {
            id: "ESC-2026-104",
            buyer: "Damascus Trade Finance House",
            seller: "Levant Sukuk Issuer SPV",
            totalAmount: 3200000,
            releasedAmount: 1600000,
            currentStage: 2,
            totalStages: 2,
            stageName: "المرحلة 2: تصفية أصول المرابحة والإيداع النهائي (50%)",
            type: "sukuk",
            status: "ACTIVE_IN_PROGRESS",
            linkedArbitration: "ARB-2026-0447"
        }
    ];

    var selectedVault = escrowVaults[0];
    var releaseCount = 0;
    var lastExportPayload = null;

    var listEl = document.getElementById("escrow-list");
    var terminalEl = document.getElementById("escrow-terminal");
    var bridge = window.SRCaseBridge;
    var bannerEl = document.getElementById("escrow-bridge-banner");

    function isFrozen(vault) {
        return vault.status === "DISPUTED_FROZEN" || vault.status === "FROZEN_BY_AWARD";
    }

    function statusTag(vault) {
        if (vault.status === "DISPUTED_FROZEN") { return "⛔ مجمد بنزاع"; }
        if (vault.status === "FROZEN_BY_AWARD") { return "⚖️ مجمد بحكم"; }
        if (vault.status === "RELEASED_BY_AWARD") { return "✅ مُفرج بحكم"; }
        if (vault.status === "PARTIALLY_RELEASED_BY_AWARD") { return "⚖️ إفراج جزئي بحكم"; }
        return "نشط";
    }

    function directiveLabel(directive) {
        return bridge ? bridge.directiveLabel(directive.action) : directive.action;
    }

    function renderBridgeBanner(vault, directive) {
        if (!bannerEl) { return; }
        if (!directive) {
            bannerEl.hidden = true;
            bannerEl.textContent = "";
            return;
        }
        bannerEl.hidden = false;
        bannerEl.className = "case-bridge-banner " + (directive.action === "FREEZE" ? "is-frozen" : "is-released");
        bannerEl.textContent = "⚖️ أمر تنفيذ وارد من مركز التحكيم (" + vault.linkedArbitration + "): " +
            directiveLabel(directive) + " • " + core.money(directive.amountEUR, "EUR") +
            " • بصمة الأمر " + String(directive.seal).slice(0, 20) + "…";
    }

    /**
     * Applies the sealed award directive of this vault's case exactly once.
     * A repeated load re-reads the balances recorded by the bridge instead of
     * releasing a second tranche, so refresh can never duplicate a payout.
     */
    function applyAwardDirective(vault) {
        if (!bridge) { return null; }
        var state = bridge.read(vault.linkedArbitration);
        var directive = state && state.directive ? state.directive : null;
        if (!directive) { return null; }

        if (vault.bridgeDirectiveSeal === directive.seal) {
            if (state.escrow && typeof state.escrow.releasedEUR === "number") {
                vault.releasedAmount = Math.min(vault.totalAmount, state.escrow.releasedEUR);
            }
            return directive;
        }

        var remaining = vault.totalAmount - vault.releasedAmount;
        var applied = 0;

        if (directive.action === "FREEZE") {
            vault.status = "FROZEN_BY_AWARD";
        } else if (directive.action === "RELEASE_ALL") {
            applied = remaining;
            vault.releasedAmount = vault.totalAmount;
            vault.status = "RELEASED_BY_AWARD";
        } else if (directive.action === "PARTIAL_RELEASE") {
            applied = Math.min(remaining, directive.amountEUR);
            vault.releasedAmount += applied;
            vault.status = (remaining - applied > 0) ? "PARTIALLY_RELEASED_BY_AWARD" : "RELEASED_BY_AWARD";
        }

        vault.bridgeDirectiveSeal = directive.seal;
        vault.bridgeDirectiveAction = directive.action;
        vault.bridgeAppliedAmount = applied;

        bridge.markDirectiveApplied(vault.linkedArbitration, directive.seal,
            directive.action + " • " + applied + " EUR released • " + vault.id);
        return directive;
    }

    function reportVaultState(vault, transaction) {
        if (!bridge) { return; }
        bridge.reportEscrow(vault.linkedArbitration, {
            escrowId: vault.id,
            buyer: vault.buyer,
            seller: vault.seller,
            status: vault.status,
            totalEUR: vault.totalAmount,
            releasedEUR: vault.releasedAmount,
            frozenEUR: isFrozen(vault) ? vault.totalAmount - vault.releasedAmount : 0,
            directiveSeal: vault.bridgeDirectiveSeal || "",
            lastTransaction: transaction || ""
        });
    }

    function renderVaults() {
        listEl.textContent = "";
        var totalAssets = 0;
        var disputedAssets = 0;

        escrowVaults.forEach(function (vault) {
            totalAssets += vault.totalAmount;
            if (isFrozen(vault)) {
                disputedAssets += (vault.totalAmount - vault.releasedAmount);
            }

            var btn = document.createElement("button");
            btn.type = "button";
            btn.className = "select-item" + (vault.id === selectedVault.id ? " active" : "");
            btn.setAttribute("aria-pressed", vault.id === selectedVault.id ? "true" : "false");
            btn.dataset.id = vault.id;

            var head = document.createElement("div");
            head.className = "item-head";

            var nameSpan = document.createElement("span");
            nameSpan.className = "item-name";
            nameSpan.textContent = vault.buyer + " ➔ " + vault.seller;

            var tagSpan = document.createElement("span");
            tagSpan.className = "item-tag mono " + (isFrozen(vault) ? "tag-red" : "");
            tagSpan.textContent = vault.id + " (" + statusTag(vault) + ")";

            head.appendChild(nameSpan);
            head.appendChild(tagSpan);

            var metaP = document.createElement("p");
            metaP.className = "item-sub";
            var remaining = vault.totalAmount - vault.releasedAmount;
            metaP.textContent = contractTypes[vault.type].label + " • الإجمالي: " + core.money(vault.totalAmount, "EUR") + " • المتبقي: " + core.money(remaining, "EUR");

            btn.appendChild(head);
            btn.appendChild(metaP);

            btn.addEventListener("click", function () {
                selectedVault = vault;
                renderVaults();
                renderBridgeBanner(selectedVault, bridge ? bridge.directiveFor(selectedVault.linkedArbitration) : null);
                renderTerminalWelcome();
            });

            listEl.appendChild(btn);
        });

        core.setText("stat-escrow-count", String(escrowVaults.length));
        core.setText("stat-escrow-total", core.money(totalAssets, "EUR"));
        core.setText("kpi-disputed-amount", core.money(disputedAssets, "EUR"));
        core.setText("active-escrow-badge", selectedVault.id);
    }

    function renderTerminalWelcome() {
        var ct = contractTypes[selectedVault.type];
        var remaining = selectedVault.totalAmount - selectedVault.releasedAmount;
        var pctReleased = Math.round((selectedVault.releasedAmount / selectedVault.totalAmount) * 100);
        var directive = bridge ? bridge.directiveFor(selectedVault.linkedArbitration) : null;

        var statusLine;
        if (selectedVault.status === "DISPUTED_FROZEN") {
            statusLine = ["log-red", "[STATUS] ⛔ FROZEN BY EMERGENCY DISPUTE LOCK • Case: " + selectedVault.linkedArbitration];
        } else if (isFrozen(selectedVault)) {
            statusLine = ["log-red", "[STATUS] ⚖️ FROZEN BY SEALED ARBITRAL AWARD • Directive seal: " + String(selectedVault.bridgeDirectiveSeal).slice(0, 20) + "…"];
        } else if (selectedVault.status === "PARTIALLY_RELEASED_BY_AWARD") {
            statusLine = ["log-gold", "[STATUS] ⚖️ PARTIALLY RELEASED BY SEALED ARBITRAL AWARD • remaining " + core.money(remaining, "EUR")];
        } else if (selectedVault.bridgeDirectiveSeal) {
            statusLine = ["log-green", "[STATUS] ✅ RELEASED BY SEALED ARBITRAL AWARD • Directive seal: " + String(selectedVault.bridgeDirectiveSeal).slice(0, 20) + "…"];
        } else {
            statusLine = ["log-green", "[STATUS] 🟢 ACTIVE & READY • Multisig vault: " + ct.multiSig];
        }

        var lines = [
            ["log-gold", "[ESCROW VAULT] Account " + selectedVault.id + " loaded."],
            ["log-blue", "[PARTIES] Buyer: " + selectedVault.buyer + " | Seller: " + selectedVault.seller],
            ["log-blue", "[CONTRACT] " + ct.label + " (" + ct.std + ")"],
            ["log-violet", "[FINANCIALS] Total: " + core.money(selectedVault.totalAmount, "EUR") + " | Released: " + core.money(selectedVault.releasedAmount, "EUR") + " (" + pctReleased + "%) | In Escrow: " + core.money(remaining, "EUR")],
            ["", "[CURRENT MILESTONE] " + selectedVault.stageName]
        ];

        if (directive) {
            lines.push(["log-gold", "[AWARD DIRECTIVE] " + directiveLabel(directive) + " • " + core.money(directive.amountEUR, "EUR") +
                " • seal " + String(directive.seal).slice(0, 20) + "… • applied " + (directive.appliedAt || "pending")]);
        }

        lines.push(statusLine);
        lines.push(["", "------------------------------------------------------------------"]);
        lines.push(["", "Choose an action: 'اعتماد الإنجاز والإفراج عن الدفعة' or 'تجميد طارئ للأصول (نزاع تحكيمي)'"]);

        core.renderLog(terminalEl, lines);
    }

    document.getElementById("btn-release-stage").addEventListener("click", function () {
        if (isFrozen(selectedVault)) {
            core.renderLog(terminalEl, [
                ["log-red", "[REJECTION] This escrow is LOCKED by a dispute freeze or a sealed arbitral award (" + selectedVault.linkedArbitration + ")."],
                ["log-red", "Funds cannot be released manually once an award directive is registered for the case."]
            ]);
            return;
        }

        if (bridge && bridge.directiveFor(selectedVault.linkedArbitration)) {
            core.renderLog(terminalEl, [
                ["log-red", "[REJECTION] A sealed award directive governs " + selectedVault.id + " (case " + selectedVault.linkedArbitration + ")."],
                ["log-red", "Manual milestone releases are disabled once the tribunal award is registered; the directive decides the payout."]
            ]);
            return;
        }

        var remaining = selectedVault.totalAmount - selectedVault.releasedAmount;
        if (remaining <= 0) {
            core.renderLog(terminalEl, [
                ["log-gold", "[COMPLETED] All milestone funds for " + selectedVault.id + " have already been released 100%."]
            ]);
            return;
        }

        var tranche = Math.min(remaining, Math.round(selectedVault.totalAmount / selectedVault.totalStages));
        selectedVault.releasedAmount += tranche;
        selectedVault.currentStage = Math.min(selectedVault.totalStages, selectedVault.currentStage + 1);

        var payload = {
            escrowId: selectedVault.id,
            action: "MILESTONE_PAYOUT_RELEASE",
            buyer: selectedVault.buyer,
            seller: selectedVault.seller,
            amountReleasedEUR: tranche,
            cumulativeReleasedEUR: selectedVault.releasedAmount,
            remainingInVaultEUR: selectedVault.totalAmount - selectedVault.releasedAmount,
            multiSigSignatures: ["0xBuyerSig...8A1", "0xInspectorSig...3F2", "0xEscrowAgentSig...C99"],
            timestamp: new Date().toISOString(),
            nonce: core.randomHex(16)
        };

        core.sha256Hex(JSON.stringify(payload)).then(function (txHash) {
            payload.transactionHash = txHash;
            lastExportPayload = payload;
            releaseCount += 1;

            core.setText("kpi-release-count", String(releaseCount));
            core.setText("stat-last-tx", txHash.slice(0, 16) + "…");
            renderVaults();
            reportVaultState(selectedVault, "MILESTONE_PAYOUT_RELEASE • " + txHash.slice(0, 16));

            core.renderLog(terminalEl, [
                ["log-gold", "[PAYOUT EXECUTION] 3-of-5 multi-sig threshold verified for " + selectedVault.id],
                ["log-green", "[RELEASED] Amount: " + core.money(tranche, "EUR") + " dispatched to " + selectedVault.seller],
                ["log-blue", "[NEW BALANCE] Vault Balance: " + core.money(selectedVault.totalAmount - selectedVault.releasedAmount, "EUR")],
                ["log-violet", "[TRANSACTION HASH] " + txHash],
                ["", "------------------------------------------------------------------"],
                ["log-green", "Milestone payout cryptographically settled. Export JSON for banking records."]
            ]);
        });
    });

    document.getElementById("btn-freeze-dispute").addEventListener("click", function () {
        selectedVault.status = "DISPUTED_FROZEN";

        var payload = {
            escrowId: selectedVault.id,
            action: "EMERGENCY_DISPUTE_FREEZE",
            buyer: selectedVault.buyer,
            seller: selectedVault.seller,
            frozenAmountEUR: selectedVault.totalAmount - selectedVault.releasedAmount,
            reason: "Notice of Arbitration filed with International Tribunal (" + selectedVault.linkedArbitration + ")",
            legalBasis: "UNCITRAL Arbitration Rules Art. 26 & Emergency Relief",
            timestamp: new Date().toISOString(),
            nonce: core.randomHex(16)
        };

        core.sha256Hex(JSON.stringify(payload)).then(function (freezeHash) {
            payload.freezeSeal = freezeHash;
            lastExportPayload = payload;

            core.setText("stat-last-tx", "FREEZE:" + freezeHash.slice(0, 12) + "…");
            renderVaults();
            reportVaultState(selectedVault, "EMERGENCY_DISPUTE_FREEZE • " + freezeHash.slice(0, 16));

            core.renderLog(terminalEl, [
                ["log-red", "[EMERGENCY DISPUTE FREEZE] ⛔ ASSETS FROZEN IMMEDIATELY"],
                ["log-gold", "[VAULT] Account: " + selectedVault.id],
                ["log-gold", "[AMOUNT LOCKED] " + core.money(payload.frozenAmountEUR, "EUR") + " secured in sovereign custody"],
                ["log-blue", "[ARBITRATION DOCKET] Linked to case: " + selectedVault.linkedArbitration],
                ["log-violet", "[CRYPTOGRAPHIC SEAL] " + freezeHash],
                ["", "------------------------------------------------------------------"],
                ["log-red", "No further releases permitted without final tribunal award or unanimous party consent."]
            ]);
        });
    });

    document.getElementById("btn-export-escrow").addEventListener("click", function () {
        if (lastExportPayload && lastExportPayload.escrowId === selectedVault.id) {
            core.downloadJSON("SR-CoreSync-Escrow-Ledger-" + selectedVault.id + ".json", lastExportPayload);
        } else {
            core.renderLog(terminalEl, [
                ["log-red", "[EXPORT NOTICE] Execute a release or freeze action first to generate the sealed transaction receipt."]
            ]);
        }
    });

    document.getElementById("new-escrow-form").addEventListener("submit", function (ev) {
        ev.preventDefault();
        var buyer = document.getElementById("f-buyer").value.trim();
        var seller = document.getElementById("f-seller").value.trim();
        var amount = parseFloat(document.getElementById("f-escrow-amount").value);
        var type = document.getElementById("f-escrow-type").value;
        var msgEl = document.getElementById("escrow-form-msg");

        if (!buyer || !seller || !amount || amount < 5000) {
            msgEl.textContent = "  ⚠️ يرجى تحديد الأطراف ومبلغ ضمان لا يقل عن €5,000";
            msgEl.style.color = "#fda4af";
            return;
        }

        var newNum = 105 + escrowVaults.length;
        var newVault = {
            id: "ESC-2026-" + newNum,
            buyer: buyer,
            seller: seller,
            totalAmount: amount,
            releasedAmount: 0,
            currentStage: 1,
            totalStages: 3,
            stageName: "الدفعة المقدمة / المرحلة 1 (30%)",
            type: type,
            status: "ACTIVE_IN_PROGRESS",
            linkedArbitration: "ARB-2026-04" + (50 + newNum % 10)
        };

        escrowVaults.push(newVault);
        selectedVault = newVault;
        renderVaults();
        renderBridgeBanner(selectedVault, bridge ? bridge.directiveFor(selectedVault.linkedArbitration) : null);
        renderTerminalWelcome();
        reportVaultState(newVault, "ESCROW_OPENED");

        msgEl.textContent = "  ✅ تم فتح محفظة الضمان " + newVault.id + " بنجاح";
        msgEl.style.color = "#6ee7b7";
        ev.target.reset();
    });

    /* Pull the sealed award directives of every vault before the first paint, so
       a case decided in the arbitration hub arrives already frozen or released. */
    (function syncFromBridge() {
        if (!bridge) { return; }

        var requested = bridge.caseIdFromQuery();
        if (requested) {
            escrowVaults.forEach(function (vault) {
                if (vault.linkedArbitration === requested) { selectedVault = vault; }
            });
        }

        escrowVaults.forEach(function (vault) {
            var directive = applyAwardDirective(vault);
            if (directive || vault === selectedVault) {
                reportVaultState(vault, "BRIDGE_SYNC");
            }
        });
    })();

    renderVaults();
    renderBridgeBanner(selectedVault, bridge ? bridge.directiveFor(selectedVault.linkedArbitration) : null);
    renderTerminalWelcome();
})();

