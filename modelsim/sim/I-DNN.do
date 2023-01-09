onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/data_in
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/start
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/clk
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/data_out
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/addr_in
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/addr_out
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/data_v
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/n_power_reset
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/reset_emulator
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/threshold_value
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/threshold_compared
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/select_threshold
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/thresh_stats
add wave -noupdate -expand -group I-DNN-TB /i_dnn_tb/data_sampled
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {0 ps} 0}
quietly wave cursor active 0
configure wave -namecolwidth 150
configure wave -valuecolwidth 100
configure wave -justifyvalue left
configure wave -signalnamewidth 0
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ps
update
WaveRestoreZoom {0 ps} {9207 ps}
