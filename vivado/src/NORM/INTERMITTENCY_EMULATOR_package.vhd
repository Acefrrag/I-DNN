package INTERMITTENCY_EMULATOR_package is 


type INTERMITTENCY_ARR_INT_TYPE is array (integer range <>) of INTEGER;

constant INTERMITTENCY_MAX_VAL_ROM_TRACE: integer := 5268;
constant INTERMITTENCY_PRESCALER: integer := 4;
constant INTERMITTENCY_NUM_ELEMNTS_ROM: integer :=  18750;


--Since I decided to infere the required voltage trrace from the DNN architecture          
                                                                --This value has to ensure the intermittent architecture can  
                                                                --correctly save the data. 
                                                                --For the intermittent DNN this time amounts to: 
                                                                --[(max_number of neuron +1) X 2] + 1 
                                                                -- 

end package;



package body INTERMITTENCY_EMULATOR_package is
end package body INTERMITTENCY_EMULATOR_package;
