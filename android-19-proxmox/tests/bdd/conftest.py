"""pytest-bdd configuration and step definition imports.

This file ensures all step definitions are loaded for pytest-bdd scenarios.
"""
# Import all step definition modules to register them with pytest-bdd
pytest_plugins = [
    "tests.bdd.step_defs.test_vm_llm_gpu_passthrough_steps",
    "tests.bdd.step_defs.test_rgb_led_control_steps",
]
