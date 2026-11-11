/* S&R CoreSync - estimator module (extracted from the master inline bundle).
   Exposes the four handlers the markup calls. Strings come from the markup,
   not from this file, so a language only supplies its own labels. */
(function () {
  'use strict';

function updateEstimatorOption(e){const t=e.dataset.group;if(!t||!_estimatorState[t])return;e.closest(".estimator-options").querySelectorAll(".estimator-option").forEach(e=>e.classList.remove("active")),e.classList.add("active"),_estimatorState[t].val=e.dataset.val,_estimatorState[t].price=parseInt(e.dataset.price)||0,_estimatorState[t].title=e.dataset.title||e.querySelector(".option-title")?.textContent||"",e.dataset.days&&(_estimatorState[t].days=e.dataset.days),"undefined"!=typeof gtag&&gtag("event","estimator_option_selected",{event_category:"Estimator",event_label:t+": "+_estimatorState[t].title,value:_estimatorState[t].price}),"undefined"!=typeof hj&&hj("event","estimator_option_selected_"+t);try{localStorage.setItem("sr_estimator_state",JSON.stringify(_estimatorState))}catch(e){}_recalcEstimator()}

function _recalcEstimator(){const e=Object.values(_estimatorState).reduce((e,t)=>e+(t.price||0),0),t=_estimatorState.type.days||"5 - 7 أيام عمل",o=document.getElementById("estimatorTotalAmount");o&&(o.style.opacity="0.4",o.style.transform="scale(0.95)",setTimeout(()=>{o.textContent=e.toLocaleString("en"),o.style.opacity="1",o.style.transform="scale(1)"},180));const s=document.getElementById("estimatorTimelineText");s&&(s.textContent=t);Object.entries({type:"summarySpecType",pages:"summarySpecPages",lang:"summarySpecLang",pay:"summarySpecPay",speed:"summarySpecSpeed"}).forEach(([e,t])=>{const o=document.getElementById(t);o&&(o.textContent=_estimatorState[e].title)})}

function bookEstimatorViaWhatsApp(){const e=Object.values(_estimatorState).reduce((e,t)=>e+(t.price||0),0),t=["*طلب تقدير مشروع جديد – S&R CoreSync*",`📦 *النوع:* ${_estimatorState.type.title}`,`📄 *النطاق:* ${_estimatorState.pages.title}`,`🌐 *اللغات:* ${_estimatorState.lang.title}`,`💳 *الدفع:* ${_estimatorState.pay.title}`,`⚡ *التسليم:* ${_estimatorState.speed.title}`,`💰 *التقدير الإجمالي: €${e.toLocaleString("en")}*`,`⏱ *المدة المتوقعة: ${_estimatorState.type.days}*`].join("%0A");window.open(`https://wa.me/31618111116?text=${encodeURIComponent(t.replace(/%0A/g,"\n"))}`,"_blank")}

function transferEstimatorToVipBooking(){const e=document.getElementById("executiveBookingModal");if(!e)return;const t=document.getElementById("bookingSessionType");t&&(t.value="creative","function"==typeof togglePackageField&&togglePackageField(t));const o=document.getElementById("bookingNotes")||document.getElementById("executiveNotes");if(o){const e=Object.values(_estimatorState).reduce((e,t)=>e+(t.price||0),0);o.value=`تقدير الحاسبة التفاعلية:\n- النوع: ${_estimatorState.type.title}\n- النطاق: ${_estimatorState.pages.title}\n- اللغات: ${_estimatorState.lang.title}\n- الدفع: ${_estimatorState.pay.title}\n- التسليم: ${_estimatorState.speed.title}\n- إجمالي التقدير: €${e.toLocaleString("en")}`}e.style.display="flex",document.body.style.overflow="hidden"}

  window.updateEstimatorOption = updateEstimatorOption;
  window.bookEstimatorViaWhatsApp = bookEstimatorViaWhatsApp;
  window.transferEstimatorToVipBooking = transferEstimatorToVipBooking;
})();
