const form = document.querySelector("#cv-form");
const addButtons = document.querySelectorAll(".add-field");
const printButton = document.querySelector("#print-cv");

addButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const group = document.querySelector(`#${button.dataset.target}`);
        const firstField = group.querySelector("label");
        const newField = firstField.cloneNode(true);
        const input = newField.querySelector("input, textarea");

        input.value = "";
        input.required = false;
        group.appendChild(newField);
        input.focus();
    });
});

if (form) {
    form.addEventListener("htmx:beforeRequest", () => {
        form.classList.add("is-loading");
    });

    form.addEventListener("htmx:afterRequest", () => {
        form.classList.remove("is-loading");
    });
}

if (printButton) {
    printButton.addEventListener("click", () => {
        const cvCard = document.querySelector("#cv-preview .cv-card");

        if (!cvCard) {
            alert("Genere ton CV avant de l'exporter.");
            return;
        }

        window.print();
    });
}
