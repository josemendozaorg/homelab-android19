# Power Optimization Role for Proxmox

This role optimizes the power consumption of the Proxmox host by:
1.  Enabling `amd-pstate` efficiency with `powersave` governor.
2.  Setting global PCIe ASPM to `powersave`.
3.  Applying `powertop` auto-tuning.
4.  **Crucially**: Disabling L1 deep-sleep for network cards to prevent connection drops.

## Manual BIOS Settings Required
To fully realize power savings (~40-60W reduction), you **MUST** apply these BIOS settings manually:

1.  **Eco Mode**:
    *   Path: `Ai Tweaker` -> `Precision Boost Overdrive` (or `Eco Mode` menu)
    *   Setting: **Eco Mode 105W** (or 65W for max savings)
2.  **Global C-State Control**:
    *   Path: `Advanced` -> `AMD CBS` -> `CPU Common Options`
    *   Setting: **Enabled**
3.  **Power Supply Idle Control**:
    *   Path: `Advanced` -> `AMD CBS` -> `CPU Common Options`
    *   Setting: **Low Current Idle**

## White Light Fix
The white VGA Q-LED on the motherboard indicates "No Monitor Detected".
*   **Fix**: Install an **HDMI Dummy Plug** into the GPU.
