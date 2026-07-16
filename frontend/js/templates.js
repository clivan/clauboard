async function loadTemplates() {

    const grid = document.getElementById("templates-grid");
    grid.innerHTML = "";

    let templates = [];

    try {
        templates = await Api.listTemplates();
    } catch (error) {
        toast(`Error cargando templates: ${error.message}`, "error");
        return;
    }

    if (!templates || templates.length === 0) {
        renderEmpty(grid, "No hay templates registrados todavía.");
        return;
    }

    for (const tpl of templates) {
        grid.appendChild(renderTemplateCard(tpl));
    }
}

function renderTemplateCard(tpl) {

    const devicesText = tpl.devices && tpl.devices.length
        ? `Dispositivos: ${tpl.devices.join(", ")}`
        : (tpl.privileged ? "Requiere privileged: true" : "Sin passthrough de dispositivos");

    return hudCard({
        title: tpl.name || tpl.id,
        id: tpl.id,
        description: `${tpl.description || ""}\n${devicesText}`,
        status: null,
        actions: [],
    });
}