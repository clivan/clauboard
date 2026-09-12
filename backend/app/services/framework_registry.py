FRAMEWORK_CHOICES = {
    "avr": {
        "baremetal": {
            "label": "Bare metal (avr-gcc)",
            "archs": ["avr"],
            "default_arch": "avr",
            "microros": False,
        },
        "freertos": {
            "label": "FreeRTOS",
            "archs": ["avr"],
            "default_arch": "avr",
            "microros": False,
        },
    },

    "msp430": {
        "baremetal": {
            "label": "Bare metal (msp430-elf-gcc)",
            "archs": ["msp430"],
            "default_arch": "msp430",
            "microros": False,
        },
        "freertos": {
            "label": "FreeRTOS",
            "archs": ["msp430"],
            "default_arch": "msp430",
            "microros": False,
        },
    },

    "stm32": {
        "baremetal": {
            "label": "Bare metal (arm-none-eabi-gcc)",
            "archs": ["arm"],
            "default_arch": "arm",
            "microros": False,
        },
        "freertos": {
            "label": "FreeRTOS",
            "archs": ["arm"],
            "default_arch": "arm",
            "microros": True,
        },
        "zephyr": {
            "label": "Zephyr RTOS",
            "archs": ["arm"],
            "default_arch": "arm",
            "microros": True,
        },
        "micropython": {
            "label": "MicroPython",
            "archs": ["arm"],
            "default_arch": "arm",
            "microros": False,
        },
    },

    "esp32": {
        "freertos": {
            "label": "FreeRTOS (incluido en ESP-IDF)",
            "archs": ["xtensa"],
            "default_arch": "xtensa",
            "microros": True,
        },
        "zephyr": {
            "label": "Zephyr RTOS (soporte parcial, ver notas)",
            "archs": ["xtensa"],
            "default_arch": "xtensa",
            "microros": True,
        },
        "micropython": {
            "label": "MicroPython",
            "archs": ["xtensa"],
            "default_arch": "xtensa",
            "microros": False,
        },
    },

    "rpi-pico": {
        "baremetal": {
            "label": "Bare metal (Pico SDK)",
            "archs": ["arm", "riscv"],
            "default_arch": "arm",
            "microros": True,
        },
        "micropython": {
            "label": "MicroPython",
            "archs": ["arm", "riscv"],
            "default_arch": "arm",
            "microros": False,
        },
        "freertos": {
            "label": "FreeRTOS (básico)",
            "archs": ["arm"],
            "default_arch": "arm",
            "microros": False,
        },
        "zephyr": {
            "label": "Zephyr RTOS (básico)",
            "archs": ["arm"],
            "default_arch": "arm",
            "microros": False,
        },
    },
}


def get_frameworks_for_template(template_id: str) -> dict:
    return FRAMEWORK_CHOICES.get(template_id, {})


def supports_microros(template_id: str, framework: str) -> bool:
    config = FRAMEWORK_CHOICES.get(template_id, {}).get(framework)
    return bool(config and config.get("microros"))


def resolve_image(
    template_id: str,
    framework: str | None,
    arch: str | None,
    microros: bool = False,
) -> str | None:
    frameworks = FRAMEWORK_CHOICES.get(template_id)
    if not frameworks:
        return None
    if not framework or framework not in frameworks:
        framework = next(iter(frameworks))
    config = frameworks[framework]
    archs = config["archs"]
    if not arch or arch not in archs:
        arch = config["default_arch"]
    suffix = "-microros" if (microros and config.get("microros")) else ""
    if len(archs) == 1:
        return f"clauboard/{template_id}-{framework}{suffix}:latest"
    return f"clauboard/{template_id}-{framework}-{arch}{suffix}:latest"