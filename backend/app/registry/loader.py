from pathlib import Path
import yaml

from app.models.plugin import Plugin


PLUGIN_ROOT = Path("/plugins")


class PluginLoader:

    def load(self):

        plugins = []

        for manifest in PLUGIN_ROOT.rglob("manifest.yaml"):

            with open(manifest, "r") as f:

                data = yaml.safe_load(f)

                plugins.append(Plugin(**data))

        return plugins