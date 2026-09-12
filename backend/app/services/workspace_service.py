from pathlib import Path


# Estructura base común a todos los templates
BASE_DIRS = ["compose", ".clauboard"]

DEPS_TARGET = (
    "deps:\n"
    "\t@mkdir -p lib\n"
    "\t@if [ -f deps.txt ]; then \\\n"
    "\t\twhile IFS= read -r url; do \\\n"
    "\t\t\t[ -z \"$$url\" ] && continue; \\\n"
    "\t\t\tcase \"$$url\" in \\\n"
    "\t\t\t\t\\#*) continue ;; \\\n"
    "\t\t\tesac; \\\n"
    "\t\t\tname=$$(basename \"$$url\" .git); \\\n"
    "\t\t\tif [ -d \"lib/$$name\" ]; then \\\n"
    "\t\t\t\techo \"lib/$$name ya existe, omitiendo\"; \\\n"
    "\t\t\telse \\\n"
    "\t\t\t\techo \"Clonando $$name (con submódulos)...\"; \\\n"
    "\t\t\t\tgit clone --depth 1 --recursive \"$$url\" \"lib/$$name\"; \\\n"
    "\t\t\tfi; \\\n"
    "\t\tdone < deps.txt; \\\n"
    "\telse \\\n"
    "\t\techo \"No hay deps.txt -- nada que resolver\"; \\\n"
    "\tfi\n"
)

DEPS_TXT_TEMPLATE = (
    "# Una URL de git por línea, ej:\n"
    "# https://github.com/adafruit/Adafruit_Sensor.git\n"
    "#\n"
    "# Corre 'make deps' para clonarlas a lib/\n"
)

STM32_DEPS_TXT_TEMPLATE = (
    "# HAL de STM32 -- descomenta la línea de tu familia y borra las\n"
    "# demás. Ambos repos usan submódulos de git; 'make deps' ya\n"
    "# clona con --recursive, no hace falta nada extra.\n"
    "#\n"
    "# STM32F103C8T6 (Blue Pill) -> familia F1\n"
    "# https://github.com/STMicroelectronics/STM32CubeF1.git\n"
    "#\n"
    "# STM32F429I-DISC1 (Discovery) -> familia F4\n"
    "# https://github.com/STMicroelectronics/STM32CubeF4.git\n"
)

MSP430_DEPS_TXT_TEMPLATE = (
    "# MSP430 DriverLib (HAL de periféricos de TI) NO tiene un\n"
    "# repositorio de git oficial -- TI lo distribuye vía MSPWare,\n"
    "# un instalador descargable desde:\n"
    "#   https://www.ti.com/tool/MSPDRIVERLIB\n"
    "#\n"
    "# Opciones:\n"
    "# 1) Descargar MSPWare manualmente y copiar la carpeta\n"
    "#    driverlib correspondiente a tu chip dentro de lib/ (no\n"
    "#    se puede automatizar con 'make deps', no es un git clone)\n"
    "# 2) Usar un fork de comunidad bajo tu propio criterio, ej:\n"
    "#    https://github.com/chintal/msp430-driverlib.git\n"
    "#    (no oficial, sin garantía de mantenimiento -- verifica que\n"
    "#    cubra tu chip antes de confiar en él)\n"
    "# 3) Programar por registros directo (sin DriverLib), como se\n"
    "#    hace comúnmente con AVR -- msp430-elf-gcc + los headers de\n"
    "#    CMSIS/device que ya trae el toolchain son suficientes para\n"
    "#    proyectos simples.\n"
)

TEMPLATES_WITH_DEPS = {"avr", "msp430", "stm32"}

TEMPLATE_CONFIG = {
    "avr": {
        "dirs": ["src", "include", "build", "lib"],
        "gitignore": "build/\nlib/\n*.elf\n*.hex\n*.map\n*.o\n*.a\n",
        "makefile": (
            "TOOLCHAIN  = avr-gcc\n"
            "MCU        = atmega328p\n"
            "F_CPU      = 16000000UL\n"
            "PROGRAMMER = usbasp\n"
            "# DEVICE solo aplica a programadores serie (bootloader\n"
            "# Arduino-compatible). USBasp/USBtinyISP son USB genérico\n"
            "# y no lo usan -- deja vacío si es tu caso.\n"
            "DEVICE    ?= $(shell grep DEVICE ../.env 2>/dev/null | cut -d= -f2)\n\n"
            "build:\n\t$(TOOLCHAIN) -mmcu=$(MCU) -DF_CPU=$(F_CPU) "
            "-Ilib -Os -o build/main.elf src/main.c\n\n"
            "flash:\n\tavrdude -p m328p -c $(PROGRAMMER) "
            "$(if $(DEVICE),-P $(DEVICE)) "
            "-U flash:w:build/main.elf\n\n"
            "fuses:\n\tavrdude -p m328p -c $(PROGRAMMER) "
            "$(if $(DEVICE),-P $(DEVICE)) -U lfuse:w:0xFF:m "
            "-U hfuse:w:0xDE:m -U efuse:w:0xFD:m\n"
            "\t# Valores de ejemplo para ATmega328P a 16MHz externo.\n"
            "\t# Verifica los tuyos en https://www.engbedded.com/fusecalc/\n"
            "\t# antes de escribir -- un fuse mal puesto puede dejar\n"
            "\t# el chip sin responder (recuperable con high-voltage\n"
            "\t# programming, pero es un dolor de cabeza evitable).\n\n"
            "clean:\n\trm -rf build/*\n\n"
            + DEPS_TARGET
        ),
    },
    "msp430": {
        "dirs": ["src", "include", "build", "lib"],
        "gitignore": "build/\nlib/\n*.elf\n*.hex\n*.map\n*.o\n*.a\n",
        "makefile": (
            "TOOLCHAIN = msp430-elf-gcc\n"
            "MCU       = msp430g2553\n"
            "DEVICE   ?= $(shell grep DEVICE ../.env 2>/dev/null | cut -d= -f2)\n\n"
            "build:\n\t$(TOOLCHAIN) -mmcu=$(MCU) -Ilib -Os "
            "-o build/main.elf src/main.c\n\n"
            "flash:\n\tmspdebug rf2500 -d $(DEVICE) "
            "'prog build/main.elf'\n\n"
            "clean:\n\trm -rf build/*\n\n"
            + DEPS_TARGET
        ),
    },
    "stm32": {
        "dirs": ["src", "include", "build", "lib"],
        "gitignore": "build/\nlib/\n*.elf\n*.hex\n*.bin\n*.map\n*.o\n*.a\n",
        "makefile": (
            "TOOLCHAIN = arm-none-eabi-gcc\n"
            "MCU       = cortex-m4\n"
            "# HAL: descomenta una línea en deps.txt según tu chip\n"
            "# (F103C8T6 -> F1, F429I-DISC1 -> F4) y corre 'make deps'.\n"
            "# Ajusta los -I de abajo a la ruta real dentro de lib/\n"
            "# una vez clonado (varía por familia).\n\n"
            "build:\n\t$(TOOLCHAIN) -mcpu=$(MCU) -Ilib -Os "
            "-o build/main.elf src/main.c\n\n"
            "flash:\n\tst-flash write build/main.bin 0x8000000\n\n"
            "debug:\n\topenocd -f interface/stlink.cfg "
            "-f target/stm32f4x.cfg\n"
            "\t# Corre esto y déjalo en foreground en una terminal.\n"
            "\t# En otra terminal (o en VS Code con F5 usando el\n"
            "\t# launch.json de .vscode/), GDB se conecta a\n"
            "\t# localhost:3333 mientras este proceso sigue vivo.\n"
            "\t# Ajusta target/stm32f4x.cfg si tu chip es F1\n"
            "\t# (target/stm32f1x.cfg) -- ej. el F103C8T6.\n\n"
            "clean:\n\trm -rf build/*\n\n"
            + DEPS_TARGET
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
        for d in BASE_DIRS + config["dirs"]:
            (project_path / d).mkdir(exist_ok=True)

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

        gitignore = project_path / ".gitignore"
        if not gitignore.exists() and config["gitignore"]:
            gitignore.write_text(config["gitignore"])
        if config["makefile"]:
            makefile = project_path / "Makefile"
            if not makefile.exists():
                makefile.write_text(config["makefile"])
        if template in TEMPLATES_WITH_DEPS:
            deps_file = project_path / "deps.txt"
            if not deps_file.exists():
                if template == "stm32":
                    content = STM32_DEPS_TXT_TEMPLATE
                elif template == "msp430":
                    content = MSP430_DEPS_TXT_TEMPLATE
                else:
                    content = DEPS_TXT_TEMPLATE
                deps_file.write_text(content)
        if template == "stm32":
            vscode_dir = project_path / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            launch_json = vscode_dir / "launch.json"
            if not launch_json.exists():
                launch_json.write_text(
                    "{\n"
                    '    "version": "0.2.0",\n'
                    '    "configurations": [\n'
                    "        {\n"
                    '            "name": "Debug STM32 (OpenOCD remoto, puerto 3333)",\n'
                    '            "type": "cortex-debug",\n'
                    '            "request": "attach",\n'
                    '            "servertype": "external",\n'
                    '            "gdbTarget": "localhost:3333",\n'
                    '            "cwd": "${workspaceFolder}",\n'
                    '            "executable": "${workspaceFolder}/build/main.elf",\n'
                    '            "showDevDebugOutput": "parsed"\n'
                    "        }\n"
                    "    ]\n"
                    "}\n"
                )