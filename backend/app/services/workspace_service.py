from pathlib import Path


# Estructura base común a todos los templates
BASE_DIRS = ["compose", ".clauboard"]

# Estructura y archivos auxiliares por template
TEMPLATE_CONFIG = {
    "avr": {
        "dirs": ["src", "include", "build"],
        "gitignore": "build/\n*.elf\n*.hex\n*.map\n*.o\n*.a\n",
        "makefile": (
            "TOOLCHAIN = avr-gcc\n"
            "MCU       = atmega328p\n"
            "F_CPU     = 16000000UL\n\n"
            "build:\n\t$(TOOLCHAIN) -mmcu=$(MCU) -DF_CPU=$(F_CPU) "
            "-Os -o build/main.elf src/main.c\n\n"
            "flash:\n\tavrdude -p m328p -c usbasp -U flash:w:build/main.elf\n\n"
            "clean:\n\trm -rf build/*\n"
        ),
    },
    "msp430": {
        "dirs": ["src", "include", "build"],
        "gitignore": "build/\n*.elf\n*.hex\n*.map\n*.o\n*.a\n",
        "makefile": (
            "TOOLCHAIN = msp430-elf-gcc\n"
            "MCU       = msp430g2553\n\n"
            "build:\n\t$(TOOLCHAIN) -mmcu=$(MCU) -Os "
            "-o build/main.elf src/main.c\n\n"
            "flash:\n\tmspdebug rf2500 'prog build/main.elf'\n\n"
            "clean:\n\trm -rf build/*\n"
        ),
    },
    "stm32": {
        "dirs": ["src", "include", "build"],
        "gitignore": "build/\n*.elf\n*.hex\n*.bin\n*.map\n*.o\n*.a\n",
        "makefile": (
            "TOOLCHAIN = arm-none-eabi-gcc\n"
            "MCU       = cortex-m4\n\n"
            "build:\n\t$(TOOLCHAIN) -mcpu=$(MCU) -Os "
            "-o build/main.elf src/main.c\n\n"
            "flash:\n\tst-flash write build/main.bin 0x8000000\n\n"
            "clean:\n\trm -rf build/*\n"
        ),
    },
    "esp32": {
        "dirs": ["src", "include", "build"],
        "gitignore": "build/\n.espressif/\nsdkconfig.old\n",
        "makefile": (
            "build:\n\tidf.py build\n\n"
            "flash:\n\tidf.py -p ${DEVICE} flash\n\n"
            "monitor:\n\tidf.py -p ${DEVICE} monitor\n\n"
            "clean:\n\tidf.py fullclean\n"
        ),
    },
    "ros2": {
        "dirs": ["src", "build", "install", "log"],
        "gitignore": "build/\ninstall/\nlog/\n*.pyc\n__pycache__/\n",
        "makefile": (
            "build:\n\tcolcon build --symlink-install\n\n"
            "source:\n\t. install/setup.bash\n\n"
            "clean:\n\trm -rf build/ install/ log/\n"
        ),
    },
    "opencv": {
        "dirs": ["src", "data", "output"],
        "gitignore": "output/\ndata/\n*.pyc\n__pycache__/\n",
        "makefile": None,
    },
    "yocto": {
        "dirs": ["layers", "conf", "build"],
        "gitignore": "build/\n*.lock\n",
        "makefile": None,
    },
}

DEFAULT_CONFIG = {
    "dirs": ["src", "data"],
    "gitignore": "build/\n*.pyc\n__pycache__/\n",
    "makefile": None,
}


class WorkspaceService:

    def initialize(self, project_path: Path, template: str = ""):

        project_path.mkdir(parents=True, exist_ok=True)

        config = TEMPLATE_CONFIG.get(template, DEFAULT_CONFIG)

        # Carpetas base + específicas del template
        for d in BASE_DIRS + config["dirs"]:
            (project_path / d).mkdir(exist_ok=True)

        # README
        readme = project_path / "README.md"
        if not readme.exists():
            readme.write_text(
                f"# {project_path.name}\n\n"
                f"Template: `{template}`\n\n"
                "## Uso\n\n"
                "```bash\n"
                "# Levantar el entorno desde Clauboard (botón Shell)\n"
                "# o manualmente:\n"
                f"docker compose --env-file .env -f compose/compose.yml run --rm {template or 'app'}\n"
                "```\n"
            )

        # .gitignore
        gitignore = project_path / ".gitignore"
        if not gitignore.exists() and config["gitignore"]:
            gitignore.write_text(config["gitignore"])

        # Makefile (solo para toolchains que lo tienen)
        if config["makefile"]:
            makefile = project_path / "Makefile"
            if not makefile.exists():
                makefile.write_text(config["makefile"])