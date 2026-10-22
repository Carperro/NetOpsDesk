"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("tool-search");
    const results = document.getElementById("search-results");
    const tools = Array.isArray(window.NETOPS_TOOLS) ? window.NETOPS_TOOLS : [];

    if (!input || !results || !requireAuth()) return;

    const moduleIcons = {
        1: "🌐",
        2: "📡",
        3: "🖥️",
        4: "🗂️",
        5: "🧰",
    };

    input.setAttribute("role", "combobox");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-haspopup", "listbox");
    input.setAttribute("aria-controls", results.id);
    input.setAttribute("aria-expanded", "false");
    results.setAttribute("role", "listbox");
    results.setAttribute("aria-live", "polite");

    function normalize(value) {
        return value
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLocaleLowerCase();
    }

    function closeResults() {
        results.hidden = true;
        input.setAttribute("aria-expanded", "false");
    }

    function renderResults() {
        const query = normalize(input.value.trim());
        results.replaceChildren();

        if (!query) {
            closeResults();
            return;
        }

        const matches = tools.filter((tool) => {
            const content = normalize(`${tool.name} ${tool.description} ${tool.module}`);
            return content.includes(query);
        }).slice(0, 8);

        if (matches.length === 0) {
            const empty = document.createElement("p");
            empty.className = "search-empty";
            empty.textContent = "No se encontraron herramientas";
            results.append(empty);
        } else {
            matches.forEach((tool) => {
                const link = document.createElement("a");
                link.className = "search-result search-option";
                link.href = tool.url;
                link.setAttribute("role", "option");

                const icon = document.createElement("span");
                icon.className = "search-result-icon";
                icon.setAttribute("aria-hidden", "true");
                icon.textContent = moduleIcons[tool.module] || "🔎";

                const text = document.createElement("span");
                text.className = "search-result-copy";

                const name = document.createElement("strong");
                name.textContent = tool.name;

                const module = document.createElement("small");
                module.textContent = `Módulo ${tool.module}`;

                text.append(name, module);
                link.append(icon, text);
                results.append(link);
            });
        }

        results.hidden = false;
        input.setAttribute("aria-expanded", "true");
    }

    input.addEventListener("input", renderResults);
    input.addEventListener("focus", () => {
        if (input.value.trim()) renderResults();
    });
    input.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeResults();
            input.blur();
        } else if (event.key === "ArrowDown" && !results.hidden) {
            event.preventDefault();
            results.querySelector("a")?.focus();
        }
    });

    results.addEventListener("keydown", (event) => {
        const links = Array.from(results.querySelectorAll("a"));
        const currentIndex = links.indexOf(document.activeElement);
        if (event.key === "Escape") {
            closeResults();
            input.focus();
        } else if (event.key === "ArrowDown" && currentIndex < links.length - 1) {
            event.preventDefault();
            links[currentIndex + 1]?.focus();
        } else if (event.key === "ArrowUp") {
            event.preventDefault();
            if (currentIndex <= 0) input.focus();
            else links[currentIndex - 1]?.focus();
        }
    });

    document.addEventListener("click", (event) => {
        if (!event.target.closest(".search-box")) closeResults();
    });
});
