function el(tag, attrs = {}, children = []) {

    const node = document.createElement(tag);

    for (const [key, value] of Object.entries(attrs)) {

        if (key === "class") node.className = value;
        else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
        else node.setAttribute(key, value);
    }

    for (const child of [].concat(children)) {

        if (child === null || child === undefined) continue;

        node.appendChild(
            typeof child === "string" ? document.createTextNode(child) : child
        );
    }

    return node;
}

function statusBadge(status) {

    const label = (status || "unknown").replace("_", " ");

    return el("span", { class: `status ${status || "unknown"}` }, [
        el("span", { class: "led" }),
        label,
    ]);
}

function hudCard({ title, id, description, status, actions }) {

    const card = el("div", { class: "card" }, [
        el("span", { class: "corner-bl" }),
        el("span", { class: "corner-br" }),
        el("div", { class: "card-header" }, [
            el("div", {}, [
                el("div", { class: "card-title" }, title),
                el("div", { class: "card-id" }, id),
            ]),
            status ? statusBadge(status) : null,
        ]),
        description ? el("div", { class: "card-desc" }, description) : null,
        el("div", { class: "card-actions" }, actions || []),
    ]);

    return card;
}

function actionButton(label, onClick, variant = "") {

    return el("button", {
        class: `btn ${variant}`.trim(),
        onclick: onClick,
    }, label);
}

function renderEmpty(container, message) {

    container.innerHTML = "";
    container.appendChild(el("div", { class: "empty" }, message));
}

function toast(message, type = "ok") {

    const node = el("div", { class: `toast ${type}` }, message);

    document.body.appendChild(node);

    setTimeout(() => node.remove(), 3500);
}

function showModal(title, content) {

    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-body").textContent = content;
    document.getElementById("modal-backdrop").hidden = false;
}

document.addEventListener("DOMContentLoaded", () => {

    document.getElementById("modal-close")
        .addEventListener("click", () => {
            document.getElementById("modal-backdrop").hidden = true;
        });
});