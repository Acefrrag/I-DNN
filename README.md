# I-DNN

Intermittent Fully-Connected Feed Forward Deep Neural Network exploiting NORM Framework

This repository contains the implementation of an emulated hardware-based reconfigurable intermittent inference application using HDL (VHDL). This repository results from the integration of [DNN](https://github.com/Acefrrag/DNN) with the [NORM emulation framework](https://github.com/simoneruffini/NORM).

## Motivation

This emulated hardware-based intermittent inference device is meant to prove NORM capabilities to enable the prototyping of user-defined architectures under different backup policies. The evaluation culminated with a performance-based characterization (DNN throughput and Power Consumption) of the harvesting scenarios (the voltage traces) in a RF energy environment.

The design of hardware-based intermittent devices takes place in the **codesign place of architectures and backup policies**. The research of the right combination architecture/backup policy is the main challenge in the design of hardware-based intermittent devices.

## Architecture

<p align="center">
  <img src="https://user-images.githubusercontent.com/59066474/232531939-2735f492-c7c6-401d-8aeb-63f4db2d42e6.png">
</p>

`I-DNN` is composed of `I-layers` connected in cascade in the same fashion of DNN. Each layer is assigned with a `NVR` from the NORM framework. The layer interface is extended to interface with the `NVR` as well as the `BACKUP_LOGIC` to receive the imperative commands. Depending on the state of the layer different data is backed up into the `NVR` (either the internal state, the output of `I-layer` or nothing in case the layer is idle). The `POWER APPROXIMATION UNITS` compute the power cycles for every `I-DNN` component for every `POWER_STATE`.

## Backup Policies

The backup policies share the behavior summarized by this high level FSM:

<p align="center">
  <img width="45%" height="45%" src="https://user-images.githubusercontent.com/59066474/232573766-2e358564-02b8-404f-9b5a-020f985bd3f0.png">
</p>

#### Save

During normal operation the backup policy may issue a backup command to the DNN architecture. If after backup the system is still under hazard condition the system is put to sleep. If no power off occurs and the voltage return to normal level the DNN perform normal operation.

Resuming normal operation means that the system will resume the inference from the layer it was being computed.

#### Recovery

After power-up the system goes to `SLEEP` mode. If the voltage goes above safety levels (above the hazard threshold) the architecture resumes the recovered inference state. 

### Dynamic Backup Policy (DB)

The dynamic backup policy sends a backup command to the I-layer every time the input voltage goes below the hazard threshold. If the voltage is still below the hazard threshold the system is put asleep to avoid performing useless progress. 

On power-up, data is recovered only if the voltage goes above safety levels to avoid performing power consuming `NV_REG` accesses in case the system powers off again.

The main assumption of this policy is that data corruption never occurs. This is ensured by performing a voltage trace analysis and offline setting up a safe hazard threshold. 

### Constant Backup Policy (CB)

The constant backup policy commands a backup when the backup counter reaches the `backup_period_clks`. A terminal counter `TC` is set and the backup command is generated. The backup command is not generated if the architecture is already below the hazard threshold, to avoid `NVR` data corruption.

### No Backup Policy

In this case the system blindly keep on executing. There is no backup, so if during an inference the system shuts down, the inference must restart from scratch.

## Reconfiguration

<p align="center">
  <img width="30%" height="30%" src="https://user-images.githubusercontent.com/59066474/232528893-ec241a78-d449-4435-bb6a-217582a46247.png">
</p>

Reconfiguration is possible thanks to using **IZyneT (Intermittent Zynet Toolchain)** based on the [Zynet package](https://github.com/dsdnu/zynet) for reconfiguration of intermittent feed forward fully connected deep neural network. The reconfiguration flow takes the MNIST dataset and the input parameters (DNN input parameters such as `num_hidden_layers`, `size` per laye etc... and the training hyperparameters such as `learning rate`, `regularization parameters` etc..) to generate the DNN model. It then generate the VHDL NORM compatible entities and VHDL compatible data (fixed point representation) and upload the vivado project.






