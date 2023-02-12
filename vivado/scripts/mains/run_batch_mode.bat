cmd /k
cd C:\Xilinx\Vivado\2020.2
settings64.bat
cd C:\Users\miche\Github_Repositories\I-DNN\vivado\scripts\mains
vivado -mode batch -source  ./tcl/DB_fixed_time_NVREG_DELAY_2_simulation_batch.tcl
