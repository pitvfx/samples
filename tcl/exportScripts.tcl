proc exportScript {} {
	global nodeOrder
	set nodeOrder {}
	foreach n [getNoOutputs] {
		getInputs $n
	}
	checkDuplicates 

	writeToFile [join $nodeOrder "\n"]
}

proc getNoOutputs {} {
	set noOutputs {}
	foreach n [nodes] {
		if {[full_name $n] == [full_name this]} {continue}
		if {[outputs $n] == 0} {
			lappend noOutputs $n
		}
	}
	return $noOutputs
}

proc outputs {node} {return [llength [dependent_nodes $node]]}
	
proc getInputs {startNode} {
	global nodeOrder
	lappend nodeOrder "$startNode"
	for {set i 0} {$i< [inputs $startNode]} {incr i} {
		set nodeInput [input $startNode $i]
		if {$nodeInput != 0} {
			getInputs $nodeInput
		} {lappend nodeOrder "push 0"}
	}

	return [dependencies $startNode]
}

proc printNode {node} {
	set nodeStr "[class $node] {"
	append nodeStr [printInputs $node] 
	append nodeStr [knobs -advw $node]\n}
	return $nodeStr
}

proc checkDuplicates {} {
	global nodeOrder
	set nodeOrder [lreverse $nodeOrder]
	foreach search $nodeOrder {
		if {![exists [full_name $search]]} {continue}
		set index [lsearch -exact $nodeOrder $search]
		set nodeStr "[printNode $search]"
		set reference false
		while {$index != -1 } {
			set nodeOrder [lreplace $nodeOrder $index $index $nodeStr]
			set nodeVar [getNodeVar $search]
			set next [lsearch -exact $nodeOrder $search]
			if {$next != -1 && !$reference} {
				set nodeOrder [linsert $nodeOrder [expr {$index+1}] "set $nodeVar \[stack 0\]"]
				set reference true
				set next [expr {$next+1}]
				}
			set index $next
			set nodeStr "push \$$nodeVar"
		}
		
	}	
}

proc lreverse {lst} {
	set reversed {}
	for {set i [llength $lst]} {[incr i -1] >= 0} {} {lappend reversed [lindex $lst $i]}
	return $reversed
}

proc getNodeVar {node} {
	set nodeVar "N"
	set l [string length $node]
	append nodeVar [string range $node [expr $l-8] $l]
	return $nodeVar
}

proc printInputs {node} {
	set total_inputs [inputs $node]
	
	# no input return when inputs == 1	
	if {$total_inputs == 1} {
		return ""
	}
	
	set maskChannel 0
	catch {if {[value $node.maskChannel] >= 0 } {set maskChannel 1}}
	
	# if node has no input or no maskChannel or has Merge in its className and only 2 inputs
	# return the inputs
	if {$total_inputs == 0 || $maskChannel == 0 || ($total_inputs == 2 && [string first "Merge" [class $node]] != -1)} {
		return "\ninputs $total_inputs"
	}
	
	return "\ninputs [expr $total_inputs-1]+1"
}

proc writeToFile {input} {
	if {[panel -w250 export {{file f f}}]} {
		set fo [open $f "w"]
		global nodeOrder
		puts $fo $input
		close $fo
	}

} 