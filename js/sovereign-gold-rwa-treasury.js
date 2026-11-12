/*
 * S&R CoreSync For Intelligent Solutions - Mission 102 - Sovereign Gold & RWA Treasury Engine
 * PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY
 * Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
 * Unauthorized copying, decompilation, redistribution, or external model training is prohibited.
 *
 * Extracted verbatim from the page's inline block (Mission 108): an external
 * script needs no CSP hash, so the published hash manifest stays shorter and
 * the engine can be cached across visits.
 */
(function () {
    'use strict';

    var activeVault = {
        code: 'AMS-VLT',
        city: 'أمستردام — هولندا (DNB Tier-IV Vault)',
        kg: 420,
        bars: '420 Bars (#NL-8801..9220)'
    };

    var assetPricesEur = {
        'SRX-AU-G': 86.40,
        'SRX-AU-KG': 86400.00,
        'SRX-RE-AMS': 1250.00,
        'SRX-SUKUK-GREEN': 1000.00
    };

    var fxRates = {
        'EUR': { rate: 1.0, symbol: '€' },
        'SAR': { rate: 4.06, symbol: 'SAR ' },
        'AED': { rate: 3.98, symbol: 'AED ' },
        'USD': { rate: 1.084, symbol: '$' },
        'SYP': { rate: 14850.0, symbol: 'SYP ' }
    };

    var vaultItems = document.querySelectorAll('.vault-item');
    var badgeEl = document.getElementById('selected-vault-badge');
    var resultEl = document.getElementById('settlement-result');
    var hashEl = document.getElementById('settlement-hash');

    vaultItems.forEach(function (item) {
        item.addEventListener('click', function () {
            vaultItems.forEach(function (v) { v.classList.remove('active'); });
            item.classList.add('active');
            activeVault.code = item.getAttribute('data-vault');
            activeVault.city = item.getAttribute('data-city');
            activeVault.kg = Number(item.getAttribute('data-kg'));
            activeVault.bars = item.getAttribute('data-bars');
            badgeEl.textContent = 'الخزينة النشطة: ' + activeVault.code;
            runSettlementSimulation();
        });
    });

    function computeSettlement() {
        var asset = document.getElementById('rwa-asset-select').value;
        var currency = document.getElementById('rwa-currency-select').value;
        var qty = Math.max(1, Number(document.getElementById('rwa-qty-input').value) || 1);
        var mode = document.getElementById('rwa-compliance-mode').value;
        var unitEur = assetPricesEur[asset] || 86.40;
        var totalEur = unitEur * qty;
        var fx = fxRates[currency] || fxRates.EUR;
        var totalConverted = totalEur * fx.rate;
        var digest = '0x' + Array.from(asset + activeVault.code + qty + mode).reduce(function (acc, ch, idx) {
            var h = ((ch.charCodeAt(0) * (idx + 17)) % 255).toString(16).padStart(2, '0');
            return acc + h;
        }, '').slice(0, 48).padEnd(48, 'a9f4');

        return {
            timestamp: new Date().toISOString(),
            vaultCode: activeVault.code,
            vaultCity: activeVault.city,
            serialRange: activeVault.bars,
            assetCode: asset,
            quantity: qty,
            currency: currency,
            totalEur: totalEur,
            totalConvertedFormatted: fx.symbol + totalConverted.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
            complianceFramework: mode,
            qabdStatus: 'QABD_HUKMI_IMMEDIATE_CONSTRUCTIVE_POSSESSION',
            baselRiskWeight: '0% Tier-1 HQLA Allocated Physical Bullion',
            merkleProofHash: digest
        };
    }

    function runSettlementSimulation() {
        var data = computeSettlement();
        resultEl.innerHTML =
            '<div><strong>✅ تم تخصيص الأصل وتسويته ذرياً (Atomic DvP Confirmed):</strong></div>' +
            '<div>• الخزينة السيادية: <strong>' + data.vaultCity + ' (' + data.vaultCode + ')</strong> — ' + data.serialRange + '</div>' +
            '<div>• الأصل والكمية: <strong>' + data.quantity + ' × ' + data.assetCode + '</strong> | القيمة الإجمالية: <strong>' + data.totalConvertedFormatted + ' (€' + data.totalEur.toLocaleString('en-US', { minimumFractionDigits: 2 }) + ')</strong></div>' +
            '<div>• المطابقة الشرعية والمصرفية: <strong>' + data.complianceFramework + ' • ' + data.qabdStatus + '</strong></div>' +
            '<div class="hash-box mono">Merkle Allocation Proof: ' + data.merkleProofHash + ' | Signed: ML-DSA-87</div>';
    }

    document.getElementById('btn-execute-dvp').addEventListener('click', runSettlementSimulation);

    document.getElementById('btn-verify-merkle').addEventListener('click', function () {
        var data = computeSettlement();
        document.getElementById('merkle-short').textContent = data.merkleProofHash.slice(0, 10) + '...' + data.merkleProofHash.slice(-4);
        runSettlementSimulation();
    });

    document.getElementById('btn-export-cert').addEventListener('click', function () {
        var cert = computeSettlement();
        var blob = new Blob([JSON.stringify(cert, null, 2)], { type: 'application/json' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'SR-CoreSync-RWA-Gold-Reserve-Certificate-' + cert.vaultCode + '.json';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    });
})();
