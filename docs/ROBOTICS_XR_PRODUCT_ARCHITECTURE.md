# Universal Matrix Robotics, XR, and Digital-Twin Product Architecture

## Purpose

This document describes the second productization layer for Universal Matrix
Spatial and Universal Matrix Robotics.

The architecture is designed so XR interfaces, robot drivers, and digital twins
share common contracts without allowing a browser, headset, or visualization
layer to command physical hardware directly.

## Control flow

```text
XR / desktop operator
        |
        v
versioned spatial protocol
        |
        v
spatial operations safety plane
        |
        v
common robot adapter contract
        |
        v
customer-specific adapter
ROS2 / CAN / CNC / simulator / OEM driver
        |
        +-------------------+
        |                   |
        v                   v
acknowledgement         robot state
                            |
                            v
                 typed digital-twin contract
                            |
                            v
                   digital-twin state store
```

## Core product modules

### `src/spatial_protocol.py`

Defines versioned messages for:

- commands;
- acknowledgements;
- telemetry;
- stop requests;
- capability discovery.

The protocol is transport neutral.

### `src/spatial_operations_control.py`

Provides bounded command validation:

- replay rejection;
- stale-command rejection;
- deadman enforcement;
- workspace bounds;
- motion limits;
- emergency-stop request propagation.

It does not authorize physical hardware execution.

### `src/robot_adapter.py`

Defines one adapter contract for downstream integrations:

- capabilities;
- current state;
- submit command;
- stop.

The same contract can back:

- ROS2;
- CAN;
- CNC;
- simulated robots;
- laboratory devices;
- OEM hardware.

### `src/xr_robot_bridge.py`

Connects XR/spatial protocol messages to the robot adapter only after the
command passes the spatial control plane.

The bridge deliberately cannot bypass validation.

### `src/digital_twin_contract.py`

Defines typed telemetry with:

- measured versus derived classification;
- units;
- source;
- timestamp;
- quality;
- calibration;
- uncertainty.

### `src/digital_twin_store.py`

Provides a bounded thread-safe in-process state/history store.

It is a reference storage layer. Production deployments can replace it with a
database or stream backend without changing the telemetry contract.

## Commercial uses

This architecture can be packaged for:

- XR robot teleoperation;
- remote maintenance;
- digital manufacturing;
- laboratory automation;
- robot fleet dashboards;
- training simulators;
- remote inspection;
- warehouse equipment;
- custom machine tools;
- OEM robotics products;
- research instrumentation.

Commercial use requires the applicable Waters Legacy Trust commercial license.

## Production buildout priorities

1. persistent PostgreSQL/TimescaleDB telemetry backend;
2. OIDC/SSO operator identity;
3. per-command authorization and entitlement checks;
4. acknowledgement timeouts and retry semantics;
5. robot-state reconciliation;
6. collision-aware planning;
7. robot-specific joint and kinematic constraints;
8. acceleration and jerk limits;
9. watchdog and heartbeat protocol;
10. signed command/audit records;
11. WebXR reference console;
12. ROS2 production adapter;
13. CAN production adapter;
14. manufacturing/CNC adapter;
15. customer-specific OEM adapter SDK.

## Safety boundary

This architecture is not a certified functional-safety system.

A production deployment must provide independent physical interlocks and
machine-specific safety engineering.

A software emergency-stop request is a request to the downstream system. It is
not equivalent to removing physical power.

## Licensing boundary

The public repository is available for permitted noncommercial use under the
PolyForm Noncommercial License 1.0.0.

Commercial products, paid services, proprietary deployments, OEM integration,
and other commercial uses require a separate Waters Legacy Trust commercial
license unless otherwise permitted by applicable law.
