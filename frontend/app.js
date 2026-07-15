function switchView(viewName) {

    for (const tab of document.querySelectorAll(".tab")) {
        tab.classList.toggle("active", tab.dataset.view === viewName);
    }

    document.getElementById("view-projects").hidden = viewName !== "projects";
    document.getElementById("view-applications").hidden = viewName !== "applications";

    if (viewName === "projects") loadProjects();
    if (viewName === "applications") loadApplications();
}

document.addEventListener("DOMContentLoaded", () => {

    for (const tab of document.querySelectorAll(".tab")) {
        tab.addEventListener("click", () => switchView(tab.dataset.view));
    }

    initProjectForm();

    // Vista inicial
    loadProjects();
});