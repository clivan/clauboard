async function loadInfrastructure() {

    const grid = document.getElementById("infrastructure-grid");
    grid.innerHTML = "";

    let services = [];

    try {
        services = await Api.listInfrastructure();
    } catch (error) {
        toast(`Error cargando infraestructura: ${error.message}`, "error");
        return;
    }

    if (!services || services.length === 0) {
        renderEmpty(grid, "No hay infraestructura registrada todavía.");
        return;
    }

    for (const svc of services) {
        grid.appendChild(renderInfrastructureCard(svc));
    }
}

function renderInfrastructureCard(svc) {

    const status = svc.status || "unknown";
    const actions = [];

    if (status === "stopped") {
        actions.push(actionButton("Start", () => runInfraAction(svc.id, "start"), "primary"));
    }

    if (status === "running") {
        actions.push(actionButton("Stop", () => runInfraAction(svc.id, "stop"), "danger"));
        actions.push(actionButton("Restart", () => runInfraAction(svc.id, "restart")));
    }

    if (status === "not_installed") {
        actions.push(actionButton("Ver infra/compose.yml", () => {
            toast("Este servicio se levanta con 'docker compose up' en infra/, no desde aquí", "error");
        }));
    }

    return hudCard({
        title: svc.name || svc.id,
        id: svc.id,
        description: svc.description || "",
        status,
        actions,
    });
}

async function runInfraAction(id, action) {

    const actionsMap = {
        start: Api.startApplication,
        stop: Api.stopApplication,
        restart: Api.restartApplication,
    };

    try {
        await actionsMap[action](id);
        toast(`${id}: ${action} OK`, "ok");
    } catch (error) {
        toast(`${id}: fallo en ${action} — ${error.message}`, "error");
    }

    loadInfrastructure();
}