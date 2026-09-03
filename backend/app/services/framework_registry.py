# Define, por template, qué frameworks/arquitecturas están disponibles,
# y cuáles de esos frameworks admiten micro-ROS como capa adicional
# (no es un framework por sí solo — es una librería que se compila
# junto con FreeRTOS o Zephyr existentes).
#
# micro-ROS NO soporta AVR ni MSP430 (8/16-bit, insuficiente e
# incompatibles con su stack). NO se puede combinar con MicroPython
# ni bare metal puro (es una librería en C que necesita un
# RTOS/scheduler de base para sus tareas internas).

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
            "microros": False,  # AVR no soportado por micro-ROS
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
            "microros": False,  # MSP430 no soportado por micro-ROS
        },
        # Sin zephyr: excluido explícitamente de la matriz de soporte
        # oficial de Zephyr (issue #87751 del propio proyecto).
        # Sin micropython: no está entre los puertos oficiales
        # (arquitectura de 16-bit distinta a los que sí soporta).
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
            "microros": True,  # soportado vía micro_ros_stm32cubemx_utils
        },
        "zephyr": {
            "label": "Zephyr RTOS",
            "archs": ["arm"],
            "default_arch": "arm",
            "microros": True,  # soportado vía micro_ros_zephyr_module
        },
        "micropython": {
            "label": "MicroPython",
            "archs": ["arm"],
            "default_arch": "arm",
            "microros": False,
        },
    },

    "esp32": {
        "baremetal": {
            "label": "Bare metal (ESP-IDF)",
            "archs": ["xtensa"],
            "default_arch": "xtensa",
            "microros": True,  # ESP-IDF ya corre sobre FreeRTOS
        },
        "freertos": {
            "label": "FreeRTOS (incluido en ESP-IDF)",
            "archs": ["xtensa"],
            "default_arch": "xtensa",
            "microros": True,  # soporte oficial, el más maduro de los 3
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
            "microros": True,  # oficial, pero SOLO transporte Serial
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
            "microros": False,  # no verificado sobre este template básico
        },
        "zephyr": {
            "label": "Zephyr RTOS (básico)",
            "archs": ["arm"],
            "default_arch": "arm",
            "microros": False,  # no verificado sobre este template básico
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
    """
    Arma el nombre de la imagen local esperada. Si microros=True y la
    combinación lo soporta, agrega el sufijo '-microros'; si no lo
    soporta, se ignora silenciosamente (no rompe, solo no lo aplica —
    el frontend no debería ofrecer el checkbox en ese caso de todos
    modos).
    """

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