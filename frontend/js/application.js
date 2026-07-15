async function loadApplications() {

    const grid = document.getElementById("applications-grid");
    grid.innerHTML = "";

    let apps = [];
    let plugins = [];

    try {
        apps = await Api.listApplications();
    } catch (error) {
        toast(`Error cargando aplicaciones: ${error.message}`, "error");
        return;
    }

    try {
        plugins = await Api.listPlugins();
    } catch (error) {
        // Los plugins son un extra (accesos directos); si fallan,
        // seguimos mostrando las aplicaciones normalmente.
        plugins = [];
    }

    if (!apps || apps.length === 0) {
        renderEmpty(grid, "No hay aplicaciones registradas todavía.");
        return;
    }

    for (const app of apps) {

        const plugin = plugins.find((p) => p.container === app.container_name);

        grid.appendChild(renderApplicationCard(app, plugin));
    }
}

function renderApplicationCard(app, plugin) {

    const status = app.status || "unknown";
    const actions = [];

    if (status === "not_installed") {
        actions.push(actionButton("Instalar", () => runAppAction(app.id, "install"), "primary"));
    }

    if (status === "stopped" || status === "not_installed") {
        actions.push(actionButton("Start", () => runAppAction(app.id, "start"), "primary"));
    }

    if (status === "running") {
        actions.push(actionButton("Stop", () => runAppAction(app.id, "stop"), "danger"));
        actions.push(actionButton("Restart", () => runAppAction(app.id, "restart")));
    }

    if (status === "running" && plugin) {
        actions.push(actionButton("Abrir ↗", () => window.open(plugin.url, "_blank"), "primary"));
    }

    if (status !== "not_installed") {
        actions.push(actionButton("Desinstalar", () => runAppAction(app.id, "uninstall"), "danger"));
    }

    return hudCard({
        title: app.name || app.id,
        id: app.id,
        description: app.description || "",
        status,
        actions,
    });
}

async function runAppAction(id, action) {

    const actionsMap = {
        install: Api.installApplication,
        start: Api.startApplication,
        stop: Api.stopApplication,
        restart: Api.restartApplication,
        uninstall: Api.uninstallApplication,
    };

    try {
        await actionsMap[action](id);
        toast(`${id}: ${action} OK`, "ok");
    } catch (error) {
        toast(`${id}: fallo en ${action} — ${error.message}`, "error");
    }

    loadApplications();
}