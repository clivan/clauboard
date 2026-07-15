import yaml

from app.config import PLUGINS_DIR
from app.models.plugin import Plugin


class PluginRepository:
    """
    Acceso al sistema de archivos. Nunca contiene lógica de negocio
    (convención del proyecto) — solo lee manifest.yml y arma Plugin.
    """

    def list(self) -> list[Plugin]:

        plugins = []

        for manifest_path in sorted(PLUGINS_DIR.glob("**/manifest.yml")):

            try:
                data = yaml.safe_load(manifest_path.read_text())
                plugins.append(Plugin(**data))

            except Exception:
                # Un manifest mal formado no debe tumbar el listado
                # completo de plugins; se ignora y sigue con el resto.
                continue

        return plugins