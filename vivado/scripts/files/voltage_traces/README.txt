Shane and Jacob recorded these 1-kHz traces on the DAQ by walking around the
PRISMS lab within about eight feet of an RFID reader.  The device being tested
was as follows: the analog front-end from an Intel DL WISP 4.1 connected to a
30 kohm resistor instead of the WISP's digital back-end.  (The MSP430F2132 in
active mode is approximately 20 kohm.)

Each line in each trace looks like this:
<time> <voltage>

The <time> field starts at an arbitrary number and counts milliseconds.  The
<voltage> field is just voltage in volts.


#Revision: Michele Pio Fragasso 04/16/2023

The voltage traces files are used to generate the VHDL compatible voltage traces
with the generation script "VoltageTrace_file_generation.py"
to be read from the Intermittency Emulator (IE) entity.


