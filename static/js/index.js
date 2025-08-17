document.addEventListener("DOMContentLoaded", () => {
  const toggleButtons = document.querySelectorAll(".WhatWeDo");
  const toggleDescriptions = document.querySelectorAll(".WhatWeDoDesc");
  const toggleSwitchers = document.querySelectorAll(".toggleSwitcher");

  toggleButtons.forEach((button, index) => {
    button.onclick = () => {
      toggleDescriptions.forEach((text, i) => {
        if (i != index) text.style.display = "none";
      });
      toggleSwitchers.forEach((swticher, i) => {
        if (i != index) swticher.style.transform = "rotate(0deg)";
      });

      const currentButton = toggleButtons[index];
      const currentDescription = toggleDescriptions[index];
      const currentSwitcher = toggleSwitchers[index];

      const isTextVisible = currentDescription.style.display === "block";
      currentDescription.style.display = isTextVisible ? "none" : "block";

      if (isTextVisible) {
        currentButton.style.backgroundColor = "#f3f3f3";
        currentButton.style.borderRadius = "45px";
      } else {
        currentButton.style.backgroundColor = "#F3F3F3";
        currentButton.style.borderRadius = "45px 45px 0px 0px";
      }

      currentSwitcher.style.transform =
        currentSwitcher.style.transform === "rotate(90deg)"
          ? "rotate(0deg)"
          : "rotate(90deg)";
    };
  });

  fetch("/api/products/")
    .then((response) => response.json())
    .then((products) => {
      const container = document.getElementById("productList");
      if (!container) {
        console.error("Контейнер для товаров не найден!");
        return;
      }

      products.forEach((product) => {
        const card = document.createElement("div");
        card.className = "productCard";

        card.innerHTML = `
            <img src="${product.image}" alt="${product.name}" class="productImage" />
            <h3 class="productName">${product.name}</h3>
            <p class="productPrice"><strong>${product.price} €</strong></p>
            <a href="/shop/${product.slug}/" class="productButton">Купить</a>


          `;

        container.appendChild(card);
      });
    })
    .catch((error) => {
      console.error("Ошибка при получении товаров:", error);
    });
});

function loadProducts(categoryId = "") {
  let url = "/api/products/";
  if (categoryId) {
    url += `?category=${categoryId}`;
  }

  fetch(url)
    .then((response) => response.json())
    .then((products) => {
      const container = document.getElementById("productList");
      container.innerHTML = "";

      if (products.length === 0) {
        container.innerHTML = "<p>Нет товаров в этой категории.</p>";
        return;
      }

      products.forEach((product) => {
        const card = document.createElement("div");
        card.className = "productCard";
        card.innerHTML = `
          <img src="${product.image}" alt="${product.name}" class="productImage" />
          <h3>${product.name}</h3>
          <p><strong>${product.price} €</strong></p>
          <button class="buyButton">
 <svg viewBox="0 0 16 16" class="bi bi-cart-check" height="24" width="24" xmlns="http://www.w3.org/2000/svg" fill="#fff">
  <path d="M11.354 6.354a.5.5 0 0 0-.708-.708L8 8.293 6.854 7.146a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0l3-3z"></path>
  <path d="M.5 1a.5.5 0 0 0 0 1h1.11l.401 1.607 1.498 7.985A.5.5 0 0 0 4 12h1a2 2 0 1 0 0 4 2 2 0 0 0 0-4h7a2 2 0 1 0 0 4 2 2 0 0 0 0-4h1a.5.5 0 0 0 .491-.408l1.5-8A.5.5 0 0 0 14.5 3H2.89l-.405-1.621A.5.5 0 0 0 2 1H.5zm3.915 10L3.102 4h10.796l-1.313 7h-8.17zM6 14a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm7 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"></path>
</svg>
  <p class="text">Buy Now</p>
</button>
        `;
        card.addEventListener("click", () => {
          window.location.href = `/shop/${product.slug}/`;
        });
        container.appendChild(card);
      });
    })

    .catch((error) => {
      console.error("Ошибка при получении товаров:", error);
    });
}

document.addEventListener("DOMContentLoaded", () => {
  loadProducts();

  document.querySelectorAll("#categoryList button").forEach((button) => {
    button.addEventListener("click", () => {
      const categoryId = button.getAttribute("data-category");
      loadProducts(categoryId);
    });
  });
});

const whyUsLink = document.querySelector(".whyUsLink");
const galleryLink = document.querySelector(".galleryLink");
const questionsLink = document.querySelector(".questions");
const adventageLink = document.querySelector(".adventageLink");
const contactUsLink = document.querySelector(".contactUsLink1");
const contactUsLink2 = document.querySelector(".contactUsLink2");
const contactUsLink3 = document.querySelector(".contactUsLink3");

const whyUsId = document.getElementById("whyUsId");
const faqBlock = document.getElementById("faqBlock");
const gallery = document.getElementById("caption1");
const adventage = document.getElementById("adventage");
const formId = document.getElementById("contactUsFormId");

whyUsLink.addEventListener("click", () => {
  document.getElementById("whyUsId").scrollIntoView({ behavior: "smooth" });
});
questionsLink.addEventListener("click", () => {
  document.getElementById("faqBlock").scrollIntoView({ behavior: "smooth" });
});
galleryLink.addEventListener("click", () => {
  document.getElementById("gallery").scrollIntoView({ behavior: "smooth" });
});
adventageLink.addEventListener("click", () => {
  document.getElementById("adventage").scrollIntoView({ behavior: "smooth" });
});
contactUsLink.addEventListener("click", () => {
  document
    .getElementById("contactUsFormId")
    .scrollIntoView({ behavior: "smooth" });
});
contactUsLink2.addEventListener("click", () => {
  document
    .getElementById("contactUsFormId")
    .scrollIntoView({ behavior: "smooth" });
});
contactUsLink3.addEventListener("click", () => {
  document
    .getElementById("contactUsFormId")
    .scrollIntoView({ behavior: "smooth" });
});
