async function loadProjects() {

    const grid = document.getElementById("projects-grid");
    grid.innerHTML = "";

    let projects = [];

    try {
        projects = await Api.listProjects();
    } catch (error) {
        toast(`Error cargando proyectos: ${error.message}`, "error");
        return;
    }

    if (!projects || projects.length === 0) {
        renderEmpty(grid, "No hay proyectos todavía. Crea el primero arriba.");
        return;
    }

    for (const project of projects) {
        const card = renderProjectCard(project, "unknown");
        grid.appendChild(card);

        // Cargar el status real en segundo plano sin bloquear el render
        Api.stackStatus(project.id)
            .then(result => {
                const badge = card.querySelector(".project-status");
                if (badge) {
                    badge.className = `status project-status ${result.status}`;
                    badge.querySelector(".led").className = "led";
                    badge.lastChild.textContent = result.status.replace("_", " ");
                }
            })
            .catch(() => {});
    }
}

function renderProjectCard(project, stackStatus = "unknown") {

    const actions = [
        actionButton("Up", () => runStackAction(project.id, "up"), "primary"),
        actionButton("Down", () => runStackAction(project.id, "down"), "danger"),
        actionButton("Restart", () => runStackAction(project.id, "restart")),
        actionButton("Shell", () => showRunCommand(project.id), "primary"),
        actionButton("Logs", () => viewStackOutput(project.id, "logs")),
        actionButton("Clonar", () => openCloneModal(project.id), ""),
        actionButton("Eliminar", () => deleteProject(project.id), "danger"),
    ];

    const statusBadgeEl = el("span", { class: `status project-status ${stackStatus}` }, [
        el("span", { class: "led" }),
        stackStatus.replace("_", " "),
    ]);

    const card = el("div", { class: "card" }, [
        el("span", { class: "corner-bl" }),
        el("span", { class: "corner-br" }),
        el("div", { class: "card-header" }, [
            el("div", {}, [
                el("div", { class: "card-title" }, project.name),
                el("div", { class: "card-id" }, project.id),
            ]),
            statusBadgeEl,
        ]),
        el("div", { class: "card-desc" }, project.description || `template: ${project.template}`),
        el("div", { class: "card-actions" }, actions),
    ]);

    return card;
}

async function showRunCommand(id) {

    try {
        const result = await Api.composeRunCommand(id);
        showModal(`${id} — shell`, result.command, true);
    } catch (error) {
        toast(`${id}: no se pudo obtener el comando — ${error.message}`, "error");
    }
}

let _cloneSourceId = null;

function openCloneModal(sourceId) {

    _cloneSourceId = sourceId;

    document.getElementById("clone-title").textContent = `CLONAR: ${sourceId}`;
    document.getElementById("clone-id").value = `${sourceId}-copy`;
    document.getElementById("clone-name").value = "";
    document.getElementById("clone-path").value = "";
    document.getElementById("clone-backdrop").hidden = false;
}

function initCloneModal() {

    document.getElementById("clone-close").addEventListener("click", () => {
        document.getElementById("clone-backdrop").hidden = true;
    });

    document.getElementById("clone-cancel").addEventListener("click", () => {
        document.getElementById("clone-backdrop").hidden = true;
    });

    document.getElementById("clone-confirm").addEventListener("click", async () => {

        const newId   = document.getElementById("clone-id").value.trim();
        const newName = document.getElementById("clone-name").value.trim();
        const newPath = document.getElementById("clone-path").value.trim();

        if (!newId || !newName) {
            toast("El ID y el nombre son obligatorios", "error");
            return;
        }

        const payload = { new_id: newId, new_name: newName };
        if (newPath) payload.new_path = newPath;

        try {
            await Api.cloneProject(_cloneSourceId, payload);
            toast(`Proyecto clonado como '${newId}'`, "ok");
            document.getElementById("clone-backdrop").hidden = true;
            loadProjects();
        } catch (error) {
            toast(`No se pudo clonar — ${error.message}`, "error");
        }
    });
}

async function runStackAction(id, action) {

    const actionsMap = {
        up: Api.composeUp,
        down: Api.composeDown,
        restart: Api.composeRestart,
    };

    try {
        await actionsMap[action](id);
        toast(`${id}: stack ${action} OK`, "ok");
    } catch (error) {
        toast(`${id}: fallo en ${action} — ${error.message}`, "error");
    }

    // Recargar proyectos para actualizar el LED
    loadProjects();
}

async function viewStackOutput(id, kind) {

    try {
        const result = kind === "logs"
            ? await Api.composeLogs(id)
            : await Api.composeStatus(id);

        const content = kind === "logs" ? result.logs : result.status;

        showModal(`${id} — ${kind}`, content || "(sin salida)");

    } catch (error) {
        toast(`${id}: no se pudo obtener ${kind} — ${error.message}`, "error");
    }
}

async function deleteProject(id) {

    if (!confirm(`¿Eliminar el proyecto "${id}"? Esta acción no se puede deshacer.`)) {
        return;
    }

    try {
        await Api.deleteProject(id);
        toast(`${id} eliminado`, "ok");
        loadProjects();
    } catch (error) {
        toast(`No se pudo eliminar ${id} — ${error.message}`, "error");
    }
}

// Defaults de device por template (mismos que EnvService en el backend)
const DEVICE_DEFAULTS = {
    msp430: "/dev/ttyACM0",
    esp32:  "/dev/ttyUSB0",
    ros2:   "/dev/video0",
};

async function populateTemplateSelect() {

    const select = document.getElementById("p-template");
    select.innerHTML = "";

    let templates = [];

    try {
        templates = await Api.listTemplates();
    } catch (error) {
        select.innerHTML = `<option value="">Error cargando templates</option>`;
        return;
    }

    if (!templates || templates.length === 0) {
        select.innerHTML = `<option value="">No hay templates registrados</option>`;
        return;
    }

    for (const tpl of templates) {
        const option = document.createElement("option");
        option.value = tpl.id;
        option.textContent = tpl.name || tpl.id;
        select.appendChild(option);
    }

    // Pre-rellenar device con el default del primer template
    updateDeviceDefault(select.value);
}

function updateDeviceDefault(templateId) {

    const deviceInput = document.getElementById("p-device");

    if (!deviceInput) return;

    const defaultDevice = DEVICE_DEFAULTS[templateId] || "";

    // Solo sobreescribir si el usuario no ha escrito algo propio
    if (!deviceInput.dataset.userEdited) {
        deviceInput.value = defaultDevice;
        deviceInput.placeholder = defaultDevice || "no aplica para este template";
    }
}

function initProjectForm() {

    const form = document.getElementById("form-new-project");
    const openBtn = document.getElementById("btn-new-project");
    const cancelBtn = document.getElementById("btn-cancel-project");
    const deviceInput = document.getElementById("p-device");

    // Marcar cuando el usuario edita el device manualmente
    deviceInput.addEventListener("input", () => {
        deviceInput.dataset.userEdited = deviceInput.value ? "1" : "";
    });

    // Actualizar device default cuando cambia el template
    document.getElementById("p-template").addEventListener("change", (e) => {
        deviceInput.dataset.userEdited = "";
        updateDeviceDefault(e.target.value);
    });

    openBtn.addEventListener("click", () => {
        form.hidden = false;
        document.getElementById("p-path").value = "";
        deviceInput.dataset.userEdited = "";
        populateTemplateSelect();
    });

    cancelBtn.addEventListener("click", () => { form.hidden = true; form.reset(); });

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const path   = document.getElementById("p-path").value.trim();
        const device = document.getElementById("p-device").value.trim();

        const payload = {
            id:          document.getElementById("p-id").value.trim(),
            name:        document.getElementById("p-name").value.trim(),
            description: document.getElementById("p-desc").value.trim(),
            template:    document.getElementById("p-template").value.trim(),
        };

        if (path)   payload.path   = path;
        if (device) payload.device = device;

        try {
            await Api.createProject(payload);
            toast(`Proyecto ${payload.id} creado`, "ok");
            form.hidden = true;
            form.reset();
            loadProjects();
        } catch (error) {
            toast(`No se pudo crear el proyecto — ${error.message}`, "error");
        }
    });
}