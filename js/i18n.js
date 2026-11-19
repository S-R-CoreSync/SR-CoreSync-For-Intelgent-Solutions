// i18n initialization using i18next
import i18next from 'i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18next
  .use(Backend)
  .use(LanguageDetector)
  .init({
    fallbackLng: 'ar',
    debug: false,
    backend: {
      loadPath: '/lang/{{lng}}.json', // files served from /lang folder
    },
    interpolation: { escapeValue: false },
  });

export default i18next;
