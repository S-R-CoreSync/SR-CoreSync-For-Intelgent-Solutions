#!/usr/bin/env bash
# =============================================================================
# PRE-PUSH GATE (بوابة ما قبل الدفع)
#
# Radical fix for the recurring pattern of CI failures: tool waves that edited
# 28-29 pages shipped with partial local verification, so byte-exact checks
# (shared sections, core metadata, og-locale) found drift only AFTER the push,
# turning CI red and forcing a fix-push cycle.
#
# Rule 6 of PLAN.md: NO push without a full green from this script.
# It runs, locally and in CI order, every blocking audit of ci.yml
# (except the three browser e2e suites, which CI runs on the pushed tree).
# Exit code 0 => safe to push. Anything else => fix locally first.
#
# Usage:  bash scripts/prepush_gate.sh
# =============================================================================
cd "$(dirname "$0")/.." || exit 1

steps=(
  "node scripts/validate.js"
  "node scripts/check_inline_scripts.mjs"
  "python scripts/audit_js_identifiers.py"
  "python scripts/check_dock_handler.py"
  "python scripts/check_command_handlers.py"
  "python scripts/audit_language_api_parity.py"
  "python scripts/audit_arabic_containment.py"
  "python scripts/audit_language_paths.py"
  "python scripts/check_script_tags.py"
  "python scripts/localize_portal_core_metadata.py --check"
  "python scripts/localize_multilingual_shared_sections.py --check"
  "python scripts/check_multilingual_page_parity.py"
  "python docs/audit_structure_vs_master.py --strict"
  "python scripts/check_content_depth_parity.py --strict"
  "python scripts/fix_og_locale.py --check"
  "python scripts/check_seo_assets.py"
  "python scripts/sentinel_i18n.py"
)

echo "PRE-PUSH GATE: ${#steps[@]} audits (CI order) + sentinel"
# إصلاح pipefail (موجة 2026-11-18): $? بعد الأنبوب كان يعكس tail دائماً فيقنّع
# أي فشل — الآن الخروج يُلتقط مباشرة من الفحص نفسه، وآخر سطر المخرجات يُطبع.
# الخطوات غير الحاجبة في ci.yml (continue-on-error) تُطبع [WARN] ولا تُحسب فاشلة
# حتى تُقلب إلى حاجبة بعد موجة مكافئة المحتوى — محاذاة حرفية مع سياسة CI.
NON_BLOCKING_RE="audit_structure_vs_master"
fail_total=0
warn_total=0
for step in "${steps[@]}"; do
  out=$(timeout 300 $step 2>&1)
  code=$?
  last_line=$(printf '%s\n' "$out" | tail -1)
  if [ $code -eq 0 ]; then
    echo "[PASS] $step"
  elif [[ "$step" =~ $NON_BLOCKING_RE ]]; then
    echo "[WARN-$code] $step (غير حاجب في ci.yml: continue-on-error)"
    echo "        آخر سطر: $last_line"
    warn_total=$((warn_total + 1))
  else
    echo "[FAIL-$code] $step"
    echo "        آخر سطر: $last_line"
    fail_total=$((fail_total + 1))
  fi
done

if [ $fail_total -eq 0 ]; then
  echo "GATE GREEN: safe to push. (${warn_total} warn غير حاجبة)"
else
  echo "GATE RED: $fail_total failing audit(s) - do NOT push."
fi
exit $fail_total
