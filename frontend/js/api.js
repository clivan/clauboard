const API_BASE = "http://localhost:8000";

async function apiRequest(path, options = {}) {

    const response = await fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });

    let body = null;

    try {
        body = await response.json();
    } catch (_) {
        body = null;
    }

    if (!response.ok) {
        const detail = body?.detail || response.statusText;
        throw new Error(detail);
    }

    return body;
}

const Api = {

    // ---- Applications ----
    listApplications: () => apiRequest("/applications"),
    listPlugins: () => apiRequest("/plugins"),
    listTemplates: () => apiRequest("/templates"),
    listInfrastructure: () => apiRequest("/infrastructure"),
    installApplication: (id) => apiRequest(`/applications/${id}/install`, { method: "POST" }),
    startApplication: (id) => apiRequest(`/applications/${id}/start`, { method: "POST" }),
    stopApplication: (id) => apiRequest(`/applications/${id}/stop`, { method: "POST" }),
    restartApplication: (id) => apiRequest(`/applications/${id}/restart`, { method: "POST" }),
    uninstallApplication: (id) => apiRequest(`/applications/${id}`, { method: "DELETE" }),

    // ---- Projects ----
    listProjects: () => apiRequest("/projects/"),
    createProject: (payload) => apiRequest("/projects/", {
        method: "POST",
        body: JSON.stringify(payload),
    }),
    deleteProject: (id) => apiRequest(`/projects/${id}`, { method: "DELETE" }),

    // ---- Project stack (docker compose) ----
    composeUp: (id) => apiRequest(`/projects/${id}/compose/up`, { method: "POST" }),
    composeDown: (id) => apiRequest(`/projects/${id}/compose/down`, { method: "POST" }),
    composeRestart: (id) => apiRequest(`/projects/${id}/compose/restart`, { method: "POST" }),
    composeLogs: (id, tail = 200) => apiRequest(`/projects/${id}/compose/logs?tail=${tail}`),
    composeStatus: (id) => apiRequest(`/projects/${id}/compose/status`),
};