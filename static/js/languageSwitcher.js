import { language } from "./language.js";

const textElements = document.querySelectorAll("[data-text]");
const submenuLinks = document.querySelectorAll(".submenu-link");

const savedLanguage = localStorage.getItem("newbornLanguage") || "ru";

const applyLanguage = (selectedLanguage) => {
  textElements.forEach((element) => {
    const textKey = element.getAttribute("data-text");
    const translatedText = language[selectedLanguage][textKey];

    if (translatedText) element.textContent = translatedText;
  });
};

applyLanguage(savedLanguage);

submenuLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    const selectedLang = link.dataset.lang;

    handleLanguageChange(selectedLang);
  });
});

const handleLanguageChange = (language) => {
  localStorage.setItem("newbornLanguage", language);
  applyLanguage(language);
};
