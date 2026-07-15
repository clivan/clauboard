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
        grid.appendChild(renderProjectCard(project));
    }
}

function renderProjectCard(project) {

    const actions = [
        actionButton("Up", () => runStackAction(project.id, "up"), "primary"),
        actionButton("Down", () => runStackAction(project.id, "down"), "danger"),
        actionButton("Restart", () => runStackAction(project.id, "restart")),
        actionButton("Logs", () => viewStackOutput(project.id, "logs")),
        actionButton("Status", () => viewStackOutput(project.id, "status")),
        actionButton("Eliminar", () => deleteProject(project.id), "danger"),
    ];

    return hudCard({
        title: project.name,
        id: project.id,
        description: project.description || `template: ${project.template}`,
        status: null,
        actions,
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

function initProjectForm() {

    const form = document.getElementById("form-new-project");
    const openBtn = document.getElementById("btn-new-project");
    const cancelBtn = document.getElementById("btn-cancel-project");

    openBtn.addEventListener("click", () => { form.hidden = false; });
    cancelBtn.addEventListener("click", () => { form.hidden = true; form.reset(); });

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const payload = {
            id: document.getElementById("p-id").value.trim(),
            name: document.getElementById("p-name").value.trim(),
            description: document.getElementById("p-desc").value.trim(),
            template: document.getElementById("p-template").value.trim(),
        };

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