const DEVICE_DEFAULTS = {
    msp430: "/dev/ttyACM0",
    esp32:  "/dev/ttyUSB0",
    ros2:   "/dev/video0",
    "rpi-pico": "/dev/ttyACM0",
};

const ARCH_LABELS = {
    arm: "ARM (Cortex-M)",
    riscv: "RISC-V (Hazard3)",
    avr: "AVR",
    msp430: "MSP430",
    xtensa: "Xtensa",
};

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

// ============================================================
// Formulario de nuevo proyecto
// ============================================================

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

    updateDeviceDefault(select.value);
    updateRos2ServicesField(select.value);
    await updateFrameworkFields(select.value);
}

function updateDeviceDefault(templateId) {

    const deviceInput = document.getElementById("p-device");

    if (!deviceInput) return;

    const defaultDevice = DEVICE_DEFAULTS[templateId] || "";

    if (!deviceInput.dataset.userEdited) {
        deviceInput.value = defaultDevice;
        deviceInput.placeholder = defaultDevice || "no aplica para este template";
    }
}

function updateRos2ServicesField(templateId) {

    const field = document.getElementById("p-ros2-services-field");

    field.hidden = (templateId !== "ros2");

    if (templateId !== "ros2") {
        document.getElementById("p-ros2-realsense").checked = false;
        document.getElementById("p-ros2-cv").checked = false;
        document.getElementById("p-ros2-gazebo").checked = false;
    }
}

async function updateFrameworkFields(templateId) {

    const frameworkField = document.getElementById("p-framework-field");
    const archField = document.getElementById("p-arch-field");
    const frameworkSelect = document.getElementById("p-framework");
    const archSelect = document.getElementById("p-arch");

    let frameworks = {};

    try {
        frameworks = await Api.getTemplateFrameworks(templateId);
    } catch (error) {
        frameworks = {};
    }

    const ids = Object.keys(frameworks);

    if (ids.length === 0) {
        frameworkField.hidden = true;
        archField.hidden = true;
        frameworkSelect.innerHTML = "";
        archSelect.innerHTML = "";
        updateMicrorosField(null);
        return;
    }

    frameworkField.hidden = false;
    frameworkSelect.innerHTML = "";

    for (const id of ids) {
        const option = document.createElement("option");
        option.value = id;
        option.textContent = frameworks[id].label || id;
        frameworkSelect.appendChild(option);
    }

    updateArchField(frameworks, frameworkSelect.value);
    updateMicrorosField(frameworks[frameworkSelect.value]);

    frameworkSelect.onchange = () => {
        updateArchField(frameworks, frameworkSelect.value);
        updateMicrorosField(frameworks[frameworkSelect.value]);
    };
}

function updateArchField(frameworks, frameworkId) {

    const archField = document.getElementById("p-arch-field");
    const archSelect = document.getElementById("p-arch");

    const config = frameworks[frameworkId];

    if (!config || !config.archs || config.archs.length <= 1) {
        archField.hidden = true;
        archSelect.innerHTML = "";
        return;
    }

    archField.hidden = false;
    archSelect.innerHTML = "";

    for (const arch of config.archs) {
        const option = document.createElement("option");
        option.value = arch;
        option.textContent = ARCH_LABELS[arch] || arch;
        if (arch === config.default_arch) option.selected = true;
        archSelect.appendChild(option);
    }
}

function updateMicrorosField(frameworkConfig) {

    const microrosField = document.getElementById("p-microros-field");
    const microrosCheckbox = document.getElementById("p-microros");

    const supported = !!(frameworkConfig && frameworkConfig.microros);

    microrosField.hidden = !supported;

    if (!supported) {
        microrosCheckbox.checked = false;
    }
}

function initProjectForm() {

    const form = document.getElementById("form-new-project");
    const openBtn = document.getElementById("btn-new-project");
    const cancelBtn = document.getElementById("btn-cancel-project");
    const deviceInput = document.getElementById("p-device");
    const templateSelect = document.getElementById("p-template");

    deviceInput.addEventListener("input", () => {
        deviceInput.dataset.userEdited = deviceInput.value ? "1" : "";
    });

    templateSelect.addEventListener("change", async (e) => {
        deviceInput.dataset.userEdited = "";
        updateDeviceDefault(e.target.value);
        updateRos2ServicesField(e.target.value);
        await updateFrameworkFields(e.target.value);
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

        const path      = document.getElementById("p-path").value.trim();
        const device    = document.getElementById("p-device").value.trim();
        const framework = document.getElementById("p-framework").value;
        const arch      = document.getElementById("p-arch").value;
        const microros  = document.getElementById("p-microros").checked;
        const templateId = document.getElementById("p-template").value.trim();

        const payload = {
            id:          document.getElementById("p-id").value.trim(),
            name:        document.getElementById("p-name").value.trim(),
            description: document.getElementById("p-desc").value.trim(),
            template:    templateId,
        };

        if (path)      payload.path      = path;
        if (device)    payload.device    = device;
        if (framework) payload.framework = framework;
        if (arch)      payload.arch      = arch;
        if (microros)  payload.microros  = true;

        if (templateId === "ros2") {
            const services = [];
            if (document.getElementById("p-ros2-realsense").checked) services.push("realsense-driver");
            if (document.getElementById("p-ros2-cv").checked) services.push("vision-processing");
            if (document.getElementById("p-ros2-gazebo").checked) services.push("gazebo");
            payload.ros2_services = services;
        }

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