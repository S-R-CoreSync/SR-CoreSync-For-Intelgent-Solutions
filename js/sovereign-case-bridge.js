/*
 * S&R CoreSync For Intelligent Solutions - Sovereign Case Bridge (Mission 107)
 * PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY
 * Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
 * Unauthorized copying, decompilation, redistribution, or external model training is prohibited.
 *
 * One case, three portals:
 *   sovereign-arbitration-hub.html   (Mission 104) issues the sealed award directive
 *   digital-forensics-litigation-hub.html (Mission 107-1) attaches sealed evidence to it
 *   smart-escrow-milestone.html      (Mission 107-2) freezes or releases the vault by it
 *
 * The site is static (GitHub Pages), so the bus is the browser itself:
 * every case lives under one namespaced localStorage key, and every write
 * dispatches `srcx:case-change` on window plus the native `storage` event for
 * other tabs. No server, no cookie, nothing leaves the device.
 *
 * External (non-inline) script: compatible with the strict hash-based CSP
 * without adding a single hash.
 */
(function (global) {
    'use strict';

    var VERSION = 1;
    var NS = 'srcx.mission107.case.';
    var EVENT = 'srcx:case-change';
    var HISTORY_LIMIT = 40;
    var EVIDENCE_LIMIT = 60;

    var DIRECTIVE = {
        FREEZE: 'FREEZE',
        PARTIAL_RELEASE: 'PARTIAL_RELEASE',
        RELEASE_ALL: 'RELEASE_ALL'
    };

    var DIRECTIVE_LABEL = {
        FREEZE: 'تجميد كامل للمتبقي في الضمان',
        PARTIAL_RELEASE: 'إفراج جزئي وتجميد المتبقي',
        RELEASE_ALL: 'إفراج كامل عن الضمان للبائع'
    };

    var ESCROW_STATUS_LABEL = {
        ACTIVE_IN_PROGRESS: 'نشط — قيد الإنجاز',
        DISPUTED_FROZEN: 'مجمّد بنزاع تحكيمي',
        FROZEN_BY_AWARD: 'مجمّد بأمر حكم',
        RELEASED_BY_AWARD: 'مُفرج عنه بأمر حكم',
        PARTIALLY_RELEASED_BY_AWARD: 'إفراج جزئي بأمر حكم'
    };

    /* ---------------------------------------------------------------------
     * Storage: localStorage when the browser allows it, an in-memory map when
     * it does not (private mode / file:// with blocked storage). The in-memory
     * map keeps a single page coherent; it is never silently mixed with disk.
     * ------------------------------------------------------------------- */
    var memory = Object.create(null);
    var storageProbe = null;

    function storage() {
        if (storageProbe !== null) { return storageProbe; }
        try {
            var s = global.localStorage;
            var probe = NS + '__probe';
            s.setItem(probe, '1');
            s.removeItem(probe);
            storageProbe = s;
        } catch (e) {
            storageProbe = false;
        }
        return storageProbe;
    }

    function normalizeCaseId(value) {
        return String(value == null ? '' : value).trim().toUpperCase();
    }

    function nowISO() {
        return new Date().toISOString();
    }

    function clone(value) {
        return JSON.parse(JSON.stringify(value));
    }

    function randomHex(bytes) {
        if (global.SRMission && global.SRMission.randomHex) {
            return global.SRMission.randomHex(bytes);
        }
        if (global.crypto && global.crypto.getRandomValues) {
            var arr = new Uint8Array(bytes);
            global.crypto.getRandomValues(arr);
            var out = '';
            for (var i = 0; i < arr.length; i++) { out += ('0' + arr[i].toString(16)).slice(-2); }
            return out;
        }
        var fallback = '';
        for (var j = 0; j < bytes; j++) { fallback += ('0' + Math.floor(Math.random() * 256).toString(16)).slice(-2); }
        return fallback;
    }

    /** Real SHA-256 through SRMission (WebCrypto), with a deterministic fallback. */
    function sha256Hex(text) {
        if (global.SRMission && global.SRMission.sha256Hex) {
            return global.SRMission.sha256Hex(text);
        }
        var h = 0x811c9dc5;
        var out = '';
        for (var round = 0; round < 8; round++) {
            for (var i = 0; i < text.length; i++) {
                h ^= text.charCodeAt(i) + round;
                h = (h * 0x01000193) >>> 0;
            }
            out += ('00000000' + h.toString(16)).slice(-8);
        }
        return Promise.resolve(out);
    }

    function emit(caseId, state) {
        var detail = { caseId: caseId, state: state };
        try {
            global.dispatchEvent(new CustomEvent(EVENT, { detail: detail }));
        } catch (e) {
            /* very old engines: listeners poll through read() instead */
        }
        return detail;
    }

    /* ---------------------------------------------------------------------
     * Records
     * ------------------------------------------------------------------- */
    function blank(caseId) {
        return {
            version: VERSION,
            caseId: caseId,
            claimant: '',
            respondent: '',
            claimAmountEUR: 0,
            disputeType: '',
            award: null,
            directive: null,
            evidence: [],
            escrow: null,
            history: [],
            createdAt: nowISO(),
            updatedAt: nowISO()
        };
    }

    function read(caseId) {
        var id = normalizeCaseId(caseId);
        if (!id) { return null; }
        var s = storage();
        var raw = null;
        if (s) {
            try { raw = s.getItem(NS + id); } catch (e) { raw = null; }
        }
        if (!raw) { raw = memory[id] || null; }
        if (!raw) { return null; }
        try {
            var parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
            return parsed && typeof parsed === 'object' ? parsed : null;
        } catch (e) {
            return null;
        }
    }

    function list() {
        var ids = Object.create(null);
        var s = storage();
        if (s) {
            try {
                for (var i = 0; i < s.length; i++) {
                    var key = s.key(i);
                    if (key && key.indexOf(NS) === 0) { ids[key.slice(NS.length)] = true; }
                }
            } catch (e) { /* ignore */ }
        }
        Object.keys(memory).forEach(function (id) { ids[id] = true; });
        return Object.keys(ids).map(read).filter(Boolean);
    }

    function write(state) {
        if (!state || !state.caseId) { throw new Error('SRCaseBridge.write requires a caseId'); }
        state.version = VERSION;
        state.updatedAt = nowISO();
        if (state.history.length > HISTORY_LIMIT) {
            state.history = state.history.slice(state.history.length - HISTORY_LIMIT);
        }
        if (state.evidence.length > EVIDENCE_LIMIT) {
            state.evidence = state.evidence.slice(state.evidence.length - EVIDENCE_LIMIT);
        }
        var payload = JSON.stringify(state);
        var s = storage();
        if (s) {
            try { s.setItem(NS + state.caseId, payload); } catch (e) { memory[state.caseId] = payload; }
        } else {
            memory[state.caseId] = payload;
        }
        emit(state.caseId, clone(state));
        return state;
    }

    function history(state, actor, action, detail) {
        state.history.push({ at: nowISO(), actor: actor, action: action, detail: detail || '' });
        return state;
    }

    function upsert(caseId) {
        var id = normalizeCaseId(caseId);
        return read(id) || blank(id);
    }

    /* ---------------------------------------------------------------------
     * Award → directive
     *
     * The rule is deliberately narrow and auditable:
     *   award >= 99.5% of the claim   -> release the vault to the seller
     *   0 < award < 99.5% of the claim -> release exactly the awarded amount,
     *                                    freeze the remainder
     *   award = 0 (claim dismissed)    -> freeze everything until the parties
     *                                    settle or a correction is filed
     * ------------------------------------------------------------------- */
    function computeDirective(awardEUR, claimAmountEUR) {
        var claim = Number(claimAmountEUR) || 0;
        var award = Number(awardEUR) || 0;
        if (award <= 0) {
            return { action: DIRECTIVE.FREEZE, amountEUR: 0 };
        }
        if (claim > 0 && award >= claim * 0.995) {
            return { action: DIRECTIVE.RELEASE_ALL, amountEUR: claim };
        }
        return { action: DIRECTIVE.PARTIAL_RELEASE, amountEUR: claim > 0 ? Math.min(award, claim) : award };
    }

    /**
     * Records a sealed draft award and derives the escrow directive from it.
     * Resolves with the stored case once the SHA-256 seal is attached.
     */
    function publishAward(input) {
        var id = normalizeCaseId(input && input.caseId);
        if (!id) { return Promise.reject(new Error('publishAward requires a caseId')); }

        var state = upsert(id);
        state.claimant = input.claimant || state.claimant || '';
        state.respondent = input.respondent || state.respondent || '';
        state.claimAmountEUR = Number(input.claimAmountEUR) || state.claimAmountEUR || 0;
        state.disputeType = input.disputeType || state.disputeType || '';

        var awardEUR = Number(input.awardEUR) || 0;
        var rule = computeDirective(awardEUR, state.claimAmountEUR);

        state.award = {
            caseId: id,
            seat: input.seat || '',
            rules: input.rules || '',
            governingLaw: input.governingLaw || '',
            claimAmountEUR: state.claimAmountEUR,
            awardEUR: awardEUR,
            meritPct: Number(input.meritPct) || 0,
            awardSeal: input.awardSeal || '',
            issuedAt: input.issuedAt || nowISO()
        };

        var body = {
            caseId: id,
            action: rule.action,
            amountEUR: rule.amountEUR,
            awardEUR: awardEUR,
            claimAmountEUR: state.claimAmountEUR,
            awardSeal: input.awardSeal || '',
            issuedAt: nowISO(),
            nonce: randomHex(8)
        };

        return sha256Hex(JSON.stringify(body)).then(function (seal) {
            state.directive = {
                caseId: id,
                action: rule.action,
                actionLabel: DIRECTIVE_LABEL[rule.action],
                amountEUR: rule.amountEUR,
                awardEUR: awardEUR,
                claimAmountEUR: state.claimAmountEUR,
                awardSeal: input.awardSeal || '',
                seal: seal,
                issuedAt: body.issuedAt,
                auto: true
            };
            history(state, 'ARBITRATION_HUB', 'AWARD_DIRECTIVE_ISSUED',
                rule.action + ' ' + rule.amountEUR + ' EUR • seal ' + seal.slice(0, 16));
            return write(state);
        });
    }

    /* ---------------------------------------------------------------------
     * Evidence (Mission 107-1)
     * ------------------------------------------------------------------- */
    function attachEvidence(caseId, evidence) {
        var id = normalizeCaseId(caseId);
        if (!id || !evidence || !evidence.id) { return null; }
        var state = upsert(id);
        var existing = null;
        for (var i = 0; i < state.evidence.length; i++) {
            if (state.evidence[i].id === evidence.id) { existing = state.evidence[i]; break; }
        }
        var record = {
            id: evidence.id,
            title: evidence.title || '',
            custodian: evidence.custodian || '',
            type: evidence.type || '',
            sizeGB: Number(evidence.sizeGB) || 0,
            capturedAt: evidence.capturedAt || '',
            seal: evidence.seal || '',
            standard: evidence.standard || '',
            attachedAt: nowISO()
        };
        if (existing) {
            state.evidence[state.evidence.indexOf(existing)] = record;
        } else {
            state.evidence.push(record);
        }
        history(state, 'FORENSICS_HUB', existing ? 'EVIDENCE_RESEALED' : 'EVIDENCE_ATTACHED',
            record.id + ' • ' + (record.seal ? record.seal.slice(0, 16) : 'unsealed'));
        return write(state);
    }

    /* ---------------------------------------------------------------------
     * Escrow (Mission 107-2)
     * ------------------------------------------------------------------- */
    function reportEscrow(caseId, snapshot) {
        var id = normalizeCaseId(caseId);
        if (!id || !snapshot) { return null; }
        var state = upsert(id);
        state.escrow = {
            escrowId: snapshot.escrowId || '',
            buyer: snapshot.buyer || '',
            seller: snapshot.seller || '',
            status: snapshot.status || '',
            statusLabel: ESCROW_STATUS_LABEL[snapshot.status] || snapshot.status || '',
            totalEUR: Number(snapshot.totalEUR) || 0,
            releasedEUR: Number(snapshot.releasedEUR) || 0,
            frozenEUR: Number(snapshot.frozenEUR) || 0,
            directiveSeal: snapshot.directiveSeal || '',
            lastTransaction: snapshot.lastTransaction || '',
            updatedAt: nowISO()
        };
        history(state, 'ESCROW_ENGINE', 'ESCROW_STATE_REPORTED',
            state.escrow.escrowId + ' • ' + state.escrow.status + ' • released ' + state.escrow.releasedEUR);
        return write(state);
    }

    function markDirectiveApplied(caseId, seal, detail) {
        var state = read(caseId);
        if (!state || !state.directive) { return null; }
        state.directive.appliedSeal = seal || state.directive.seal;
        state.directive.appliedAt = nowISO();
        history(state, 'ESCROW_ENGINE', 'DIRECTIVE_APPLIED', detail || state.directive.action);
        return write(state);
    }

    /* ---------------------------------------------------------------------
     * Reader helpers
     * ------------------------------------------------------------------- */
    function directiveFor(caseId) {
        var state = read(caseId);
        return state && state.directive ? state.directive : null;
    }

    function directiveLabel(action) {
        return DIRECTIVE_LABEL[action] || action || '';
    }

    function escrowStatusLabel(status) {
        return ESCROW_STATUS_LABEL[status] || status || '';
    }

    function summary(caseId) {
        var state = read(caseId);
        if (!state) {
            return {
                caseId: normalizeCaseId(caseId), found: false,
                evidenceCount: 0, evidenceSealed: 0,
                escrowStatus: '', escrowStatusLabel: 'لا سجل ضمان مرتبط',
                directive: null, directiveLabel: ''
            };
        }
        var sealed = state.evidence.filter(function (item) { return !!item.seal; }).length;
        return {
            caseId: state.caseId,
            found: true,
            evidenceCount: state.evidence.length,
            evidenceSealed: sealed,
            escrowStatus: state.escrow ? state.escrow.status : '',
            escrowStatusLabel: state.escrow ? (state.escrow.statusLabel || escrowStatusLabel(state.escrow.status)) : 'لم يُبلَّغ أي ضمان بعد',
            escrow: state.escrow,
            directive: state.directive,
            directiveLabel: state.directive ? directiveLabel(state.directive.action) : '',
            award: state.award
        };
    }

    function subscribe(handler) {
        if (typeof handler !== 'function') { return function () { }; }
        function onLocal(ev) {
            if (ev && ev.detail && ev.detail.caseId) { handler(ev.detail.caseId, ev.detail.state); }
        }
        function onStorage(ev) {
            if (!ev || !ev.key || ev.key.indexOf(NS) !== 0) { return; }
            var id = ev.key.slice(NS.length);
            handler(id, read(id));
        }
        global.addEventListener(EVENT, onLocal);
        global.addEventListener('storage', onStorage);
        return function () {
            global.removeEventListener(EVENT, onLocal);
            global.removeEventListener('storage', onStorage);
        };
    }

    function caseIdFromQuery(param) {
        var name = param || 'case';
        try {
            var value = new URLSearchParams(global.location.search).get(name);
            return value ? normalizeCaseId(value) : '';
        } catch (e) {
            return '';
        }
    }

    function urlFor(page, caseId) {
        var id = normalizeCaseId(caseId);
        return page + (id ? '?case=' + encodeURIComponent(id) : '');
    }

    global.SRCaseBridge = {
        VERSION: VERSION,
        NAMESPACE: NS,
        EVENT: EVENT,
        DIRECTIVE: DIRECTIVE,
        read: read,
        list: list,
        write: write,
        computeDirective: computeDirective,
        publishAward: publishAward,
        attachEvidence: attachEvidence,
        reportEscrow: reportEscrow,
        markDirectiveApplied: markDirectiveApplied,
        directiveFor: directiveFor,
        directiveLabel: directiveLabel,
        escrowStatusLabel: escrowStatusLabel,
        summary: summary,
        subscribe: subscribe,
        caseIdFromQuery: caseIdFromQuery,
        urlFor: urlFor,
        normalizeCaseId: normalizeCaseId,
        sha256Hex: sha256Hex
    };
})(window);
