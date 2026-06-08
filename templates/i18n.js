i18next
  .use(i18nextBrowserLanguageDetector)
  .init({
    fallbackLng: 'en',
    debug: false,
    resources: {
      en: {
        translation: {}
      },
      ta: {
        translation: {}
      }
    }
  }, function() {
    updateContent();
  });

function updateContent() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    el.innerHTML = i18next.t(el.getAttribute("data-i18n"));
  });
}

/*i18next.init({
  lng: 'en',
  fallbackLng: 'en',
  backend: {
    loadPath: '/locales/{{lng}}/translation.json'
  }
}, updateContent);*/

// Initialize i18next
i18next
  .use(i18nextHttpBackend)   // load JSON files
  .init({
    lng: 'en',               // default language
    fallbackLng: 'en',

    debug: false,

    backend: {
      loadPath: '/static/locales/{{lng}}/translation.json'
    }

  }, function () {
    updateContent();
  });


// Apply translations to page
function updateContent() {

  // normal text
  document.querySelectorAll("[data-i18n]").forEach(el => {
    el.innerHTML = i18next.t(el.dataset.i18n);
  });

  // placeholders
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    el.placeholder = i18next.t(el.dataset.i18nPlaceholder);
  });

  // input button values
  document.querySelectorAll("[data-i18n-value]").forEach(el => {
    el.value = i18next.t(el.dataset.i18nValue);
  });

}


// Language switch function
function changeLang(lang) {
  i18next.changeLanguage(lang, updateContent);
}
