# ###############################################################
# Guillaume W. Bres, 2016            <guillaume.bres@noisext.com>
#################################################################
# package_ip.tcl
# packages specified IP core using the Xilinx IP packager 
# supports reference to one library
# supports reference to N cores from the given library
# includes all .xci files as embedded cores
#####
# TODO: support AXI4 memory mapping
#	set_property base_address 0x43BE0000 \
#        [ipx::get_address_blocks reg0 -of_objects \
#              [ipx::get_memory_maps s_axi -of_objects [ipx::current_core]]]
#	set_property range 4096 \
#        [ipx::get_address_blocks reg0 -of_objects \
#              [ipx::get_memory_maps s_axi -of_objects [ipx::current_core]]]
#################################################################

# following interfaces will be automatically created
set IP_XACT_AUTO_INFERRED_BUSIFS [list \
	"xilinx.com:interface:axis_rtl:1.0" \
	"xilinx.com:signal:clock_rtl:1.0"]

# packager env
set VENDOR ""
set COMPANY_URL "www.noisext.com"
set PART xc7z045ffg900-2

# ip definition
set IP_NAME ""
set IP_REPO ""
set IP_VERSION ""

# subcore ref.
set subcore_references "" 

# command line
set args [split "$argv" " "]
set len [llength $args]
puts "command line $argv"
set k 0
while {$k < $len} {

	set arg [lindex $args $k]
	set splitted [split $arg "=" ]
	set key [lindex $splitted 0]
	set value [lindex $splitted 1]

	switch -exact $key {
		
		--vendor {
			set VENDOR "$value"
		}

		--ip_name {
			set IP_NAME "$value"
		}

		--ip_repo {
			set IP_REPO "$value"
		}

		--ip_version {
			set IP_VERSION "$value"
		}

		--subcore {
			lappend subcore_references $value
		}
	}

	set k [expr $k+1]
}

# make sure all mandatory flags are set
if {$VENDOR == ""} {
	puts "\n--vendor must be defined"
	exit -1
} elseif {($IP_NAME == "" )||($IP_VERSION == "")} {
	puts "\nIP is not properly defined"	
	puts "flags --ip_name --ip_version must be set"
	exit -1
} else {
	puts "\nvendor $VENDOR"
	puts "packaging ip $IP_NAME"
}

# temporary project is created in /tmp
puts "\ncreating temporary project"
create_project packager /tmp/ip_packager -force -part $PART -ip
set_property ip_repo_paths $IP_REPO [current_project]
set_property top $IP_NAME.vhd [current_fileset]
set_property target_language VHDL [current_project]

# ip sources
puts "\nadding source files"
add_files [glob -nocomplain -type f $IP_NAME/src/*.vhd]

# add existing simulation files
set exists [file exists $IP_NAME/simulation]
if {$exists == 1} {
	puts "\nadding simulation file set\n"
	add_files -fileset sim_1 [glob -nocomplain -type f $IP_NAME/simulation/*]
	foreach simfile [glob -nocomplain -type f $IP_NAME/simulation/*] {
		set filename [lindex [split $simfile "/"] end]
		set_property top $filename [get_filesets sim_1]
		set_property top_lib xil_defaultlib [get_filesets sim_1]
	}
}

# add possible embedded .xci files
set subdirs [glob -nocomplain -type d $IP_NAME/src/*]
foreach dir $subdirs {
	set xci_core [glob -nocomplain -type f $dir/*.xci]
	puts "found subcore: $xci_core"
	import_files -fileset sources_1 $xci_core
}

# add possible .xdc files
set subdirs [glob -nocomplain -type d $IP_NAME]
foreach dir $subdirs {
	if {[string match $dir "constraints"]} {
		set constraint_files [glob -nocomplain -type f $dir/*.xdc]
		foreach xdc $constraint_files {
			add_files -fileset constrs_1 $xdc			
			# set_property USED_IN {synthesis implementation out_of_context} $ooc_constraint_file
		}
	}
}

# add possible .coe files
set coe_files [glob -nocomplain -type f $IP_NAME/src/*.coe]
foreach coe $coe_files {
	import_files -fileset sources_1 $coe
}

update_compile_order -fileset sim_1
update_compile_order -fileset sources_1
update_compile_order -fileset constrs_1

# move to ip-packager
puts "\nip-packager\n"
ipx::package_project -force -import_files -root_dir $IP_NAME
set core [ipx::current_core]

# automatically infer all busif in env. variable
puts "\nbus interfaces auto inferrence\n"
foreach busif $IP_XACT_AUTO_INFERRED_BUSIFS {
	puts "\nauto-inferring $busif\n"
	ipx::infer_bus_interfaces $busif [ipx::current_core]
}

puts "\nBus interfaces definition\n"
set clock_busifs [ipx::get_bus_interfaces -filter {BUS_TYPE_NAME == "clock"}]
set axis_busifs [ipx::get_bus_interfaces -filter {BUS_TYPE_NAME == "axis"}]

# putting all axis busif names together so they can be associated to ap_clk
set first_axis_busif [lindex $axis_busifs 0]
foreach axis_busif $axis_busifs {
	set busif_name [lindex [split $axis_busif " "] 2]
	if {$axis_busif == $first_axis_busif} {
		set axis_concat_busif_names "$busif_name"
	} else {
		set axis_concat_busif_names "$axis_concat_busif_names:$busif_name"
	}
}

# 'ap_clk'/'ap_clock'/'clk' signal will
# clock all AXI4S interfaces
foreach clockif $clock_busifs {
	ipx::add_bus_parameter ASSOCIATED_BUSIF $clockif
	set clock_busif_name [lindex [split $clockif " "] 2]
	set is_ap_clk_busif [string match $clock_busif_name "ap_clk"]
	set is_ap_clock_busif [string match $clock_busif_name "ap_clock"]
	set is_clk_busif [string match $clock_busif_name "clk"]
	if {($is_ap_clk_busif == 1)||($is_ap_clock_busif == 1)||($is_clk_busif == 1)} {
		set_property value $axis_concat_busif_names [ipx::get_bus_parameters ASSOCIATED_BUSIF -of_objects $clockif]
	}
}

puts "\nIP definition"
set_property display_name $IP_NAME $core
set_property vendor $VENDOR $core
set_property vendor_display_name $VENDOR $core
set_property description $IP_NAME $core
set_property version $IP_VERSION $core

puts "\nadding subcore references"
foreach subcore $subcore_references {
	puts "adding reference to $subcore"
	ipx::add_subcore $subcore [ipx::get_file_groups xilinx_anylanguagesynthesis -of_objects $core]
	ipx::add_subcore $subcore [ipx::get_file_groups xilinx_anylanguagebehavioralsimulation -of_objects $core]
}

update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

puts "\nuser parameters"
set bitString_typed_parameters [ipx::get_user_parameters -filter {VALUE_FORMAT == "bitString"}]
set long_typed_parameters [ipx::get_user_parameters -filter {VALUE_FORMAT == "long"}]
set tlast_ports [ipx::get_ports -filter {Name =~ "*tlast" }]
set tready_ports [ipx::get_ports -filter {Name =~ "*tready" }]

# restrain user-parameters with `bitString` type
foreach bitString_param $bitString_typed_parameters {
	set param_name [lindex [split $bitString_param " "] 2]
	set_property widget {comboBox} [ipgui::get_guiparamspec -name "$param_name" -component $core]
	set_property value_validation_list {{"0"} {"1"}} $bitString_param
	
	set is_tready [string match $param_name "SUPPORT_TREADY"]
	if {$is_tready == 1} {
		set_property tooltip {"Allow core to be stalled"} [ipgui::get_guiparamspec -name "$param_name" -component $core]

		foreach port $tready_ports {
			set direction [get_property Direction $port]
			if {$direction == "in"} {
				set_property driver_value 0 $port
			}
			set new_property "spirit:decode(id('MODELPARAM_VALUE.$param_name')) = \"1\""
			set_property enablement_dependency $new_property $port
		}
	}
	set is_tlast [string match $param_name "SUPPORT_TLAST"]
	if {$is_tlast == 1} {
		set_property tooltip {"Route/generate TLAST"} [ipgui::get_guiparamspec -name "$param_name" -component $core]
		
		foreach port $tlast_ports {
			set direction [get_property Direction $port]
			if {$direction == "in"} {
				set_property driver_value 0 $port
			}
			set new_property "spirit:decode(id('MODELPARAM_VALUE.$param_name')) = \"1\""
			set_property enablement_dependency $new_property $port
		}
	}
}

# add existing documentation 
puts "adding IP documentation"
set subdirs [glob -nocomplain -type d $IP_NAME/*]
foreach dir $subdirs {
	if {[string match $dir "$IP_NAME/doc"]} {
		set docfiles [glob -nocomplain -type f $IP_NAME/doc/*]
		foreach docfile $docfiles {
			set extension [lindex [split $docfile "."] end]
			if {$extension == "tex"} {
				# found latex file, determine pdf name
				set filename [lindex [split [lindex [split $docfile "/"] end] "."] 0] 
				set product_guide doc/$filename.pdf
				# create product-guide group
				ipx::add_file_group -type product_guide {} $core
				# add product-guide
				ipx::add_file $product_guide [ipx::get_file_groups xilinx_productguide -of_objects $core]
				set_property type pdf [ipx::get_files $product_guide -of_objects [ipx::get_file_groups xilinx_productguide -of_objects $core]]
			} elseif {$extension == "txt"} {
				# found changelog file
				set filename [lindex [split [lindex [split $docfile "/"] end] "."] 0] 
				set version_log doc/$filename.txt
				# create versionning group
				ipx::add_file_group -type version_info {} $core
				# add version log
				ipx::add_file $version_log [ipx::get_file_groups xilinx_versioninformation -of_objects $core]
				set_property type text [ipx::get_files $version_log -of_objects [ipx::get_file_groups xilinx_versioninformation -of_objects $core]]
			}
		}
	}
}

# ip integrity
ipx::check_integrity $core

# packaging
puts "\npackaging ip"
ipx::create_xgui_files $core
ipx::update_checksums $core 
ipx::save_core $core 
update_ip_catalog

puts "\nip $IP_NAME has been packaged" 
exit 0
