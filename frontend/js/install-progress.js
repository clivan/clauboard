const InstallProgress = (() => {

    let _source = null;

    function show(appName) {

        document.getElementById("install-bar-label").textContent =
            `Instalando ${appName}...`;
        document.getElementById("install-bar-fill").style.width = "0%";
        document.getElementById("install-bar-pct").textContent = "0%";
        document.getElementById("install-bar").hidden = false;
    }

    function update(percent, progress) {

        const pct = Math.min(percent, 100);
        document.getElementById("install-bar-fill").style.width = `${pct}%`;
        document.getElementById("install-bar-pct").textContent = `${pct}%`;

        if (progress) {
            document.getElementById("install-bar-label").textContent =
                progress;
        }
    }

    function hide() {

        document.getElementById("install-bar").hidden = true;

        if (_source) {
            _source.close();
            _source = null;
        }
    }

    function start(appId, appName) {

        return new Promise((resolve) => {

            if (_source) {
                _source.close();
            }

            show(appName);

            _source = new EventSource(
                `http://localhost:8000/applications/${appId}/install/progress`
            );

            _source.onmessage = (event) => {

                try {
                    const data = JSON.parse(event.data);

                    if (data.status === "done" || data.status === "error") {
                        hide();
                        resolve(data.status === "done");
                        return;
                    }

                    if (data.percent !== undefined) {
                        update(data.percent, data.progress);
                    }

                } catch (_) { /* ignorar eventos malformados */ }
            };

            _source.onerror = () => {
                hide();
                resolve(false);
            };
        });
    }

    return { start, hide };

})();