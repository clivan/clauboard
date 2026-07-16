const VIEWS = ["projects", "applications", "templates", "infrastructure"];

function switchView(viewName) {

    for (const tab of document.querySelectorAll(".tab")) {
        tab.classList.toggle("active", tab.dataset.view === viewName);
    }

    for (const view of VIEWS) {
        document.getElementById(`view-${view}`).hidden = viewName !== view;
    }

    if (viewName === "projects") loadProjects();
    if (viewName === "applications") loadApplications();
    if (viewName === "templates") loadTemplates();
    if (viewName === "infrastructure") loadInfrastructure();
}

document.addEventListener("DOMContentLoaded", () => {

    for (const tab of document.querySelectorAll(".tab")) {
        tab.addEventListener("click", () => switchView(tab.dataset.view));
    }

    initProjectForm();

    // Vista inicial
    loadProjects();
});