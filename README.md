# I-DNN
Intermittent Deep Neural Network exploiting NORM Framework

This repository contains the implementation of an emulated hardware-based reconfigurable intermittent inference application using HDL (VHDL). This repository results from the integration of [DNN](https://github.com/Acefrrag/DNN) with the [NORM emulation framework](https://github.com/simoneruffini/NORM).

## Architecture 

<p align="center">
  <img src="https://user-images.githubusercontent.com/59066474/232524212-5024eab5-739c-4894-be2d-8ad3d4fb2b4d.png")>
</p>

`I-DNN` is composed of `I-layers` connected in cascade in the same fashion of DNN. Each layer is assigned with a `NVR` from the NORM framework. The layer interface is extended to interface with the non-volatile memory as well as the `BACKUP_LOGIC` to receive the imperative commands. Depending on the state of the layer different data is backed up into the `NVR` (either the internal state, the output of `I-layer` or nothing in case the layer is idle).

## Reconfiguration


<p align="center">
  <img src="https://user-images.githubusercontent.com/59066474/232528893-ec241a78-d449-4435-bb6a-217582a46247.png




## Motivation

This emulated hardware-based intermittent inference device is meant to prove NORM capabilities of evaluation of user-defined architectures under different backup policies. 




