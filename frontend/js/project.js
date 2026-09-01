// Defaults de device por template (mismos que EnvService en el backend)
const DEVICE_DEFAULTS = {
    msp430: "/dev/ttyACM0",
    esp32:  "/dev/ttyUSB0",
    ros2:   "/dev/video0",
    "rpi-pico": "/dev/ttyACM0",
};

const ARCH_LABELS = { arm: "ARM (Cortex-M)", riscv: "RISC-V (Hazard3)" };

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

    frameworkSelect.onchange = () => updateArchField(frameworks, frameworkSelect.value);
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

        const payload = {
            id:          document.getElementById("p-id").value.trim(),
            name:        document.getElementById("p-name").value.trim(),
            description: document.getElementById("p-desc").value.trim(),
            template:    document.getElementById("p-template").value.trim(),
        };

        if (path)      payload.path      = path;
        if (device)    payload.device    = device;
        if (framework) payload.framework = framework;
        if (arch)      payload.arch      = arch;

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