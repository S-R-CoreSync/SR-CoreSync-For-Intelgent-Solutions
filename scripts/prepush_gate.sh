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
# (except the three browser e2e suites, which CI runs on the pushed tree),
# plus the backend/API test suite (pytest) so regressions there block a push too.
# Exit code 0 => safe to push. Anything else => fix locally first.
#
# Usage:  bash scripts/prepush_gate.sh
# =============================================================================
cd "$(dirname "$0")/.." || exit 1

# [2026-11-26] مفسّر بايثون صريح: على Windows/Git Bash تختلط ثلاثة مفسّرات
# (AutoClaw المرفق، .venv، النظام) فيفشل الفحص بخطأ «ملف غير موجود» أو 127
# رغم وجود الملف. نُثبّت مفسّر المشروع أولاً حتى تكون البوابة قابلة للتنفيذ حرفياً
# كما تقتضي القاعدة 6 (كانت تعمل في CI على Linux فقط).
if [ -x ".venv/Scripts/python.exe" ]; then
  PY=".venv/Scripts/python.exe"
elif [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
else
  PY="$(command -v python3 || command -v python || echo python)"
fi
echo "PRE-PUSH GATE: python = $PY"

steps=(
  "node scripts/validate.js"
  "node scripts/check_inline_scripts.mjs"
  "$PY scripts/audit_js_identifiers.py"
  "$PY scripts/check_dock_handler.py"
  "$PY scripts/check_command_handlers.py"
  "$PY scripts/audit_language_api_parity.py"
  "$PY scripts/audit_arabic_containment.py"
  "$PY scripts/audit_language_paths.py"
  "$PY scripts/check_script_tags.py"
  "$PY scripts/localize_portal_core_metadata.py --check"
  "$PY scripts/localize_multilingual_shared_sections.py --check"
  "$PY scripts/check_multilingual_page_parity.py"
  "$PY docs/audit_structure_vs_master.py --strict"
  "$PY scripts/check_content_depth_parity.py --strict"
  "$PY scripts/fix_og_locale.py --check"
  "$PY scripts/check_seo_assets.py"
  # [2026-11-26 — الاقتراح 29] سلامة الروابط والأصول على مجموعة النشر الفعلية:
  # الفحص القديم كان يقرأ href/src فقط، فمرّت 55 صورة مكسورة (مسارات لغات +
  # srcset مسطّح) دون أن يراها أحد. الآن يُبنى العرف الكامل ويُفحص كل مرشّح srcset.
  "$PY scripts/prepare_publish_set.py"
  "$PY scripts/check_site_links.py"
  "$PY scripts/sentinel_i18n.py"
  # [2026-11-26 — الاقتراح 23] اختبارات الخلفية/ـAI: كانت 230 اختباراً خارج البوابة،
  # فأي انحدار خلفي لا يوقف الدفع. تُشغّل بمفسّر المشروع نفسه.
  "$PY -m pytest tests -q"
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
  # [2026-11-27] 300s كانت تضيّق على السنتينل على ويندوز تحت حِمل (قِيس 396s
  # مقابل 128s في تشغيل هادئ) فيسقط بمهلة 124 لا بفشل حقيقي. المهلة liveness لا صحّة.
  out=$(timeout 600 $step 2>&1)
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
