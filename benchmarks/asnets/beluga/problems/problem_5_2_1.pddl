(define
	(problem test)
	(:domain beluga)
  (:objects
		t1 - beluga-truck
		t2 - fab-truck
		rack1 - rack
		rack2 - rack
		part1 - part
		part2 - part
		part3 - part
		part4 - part
		part5 - part
		plA - production-line
		n03 - num
		n06 - num
		n07 - num
		n09 - num
		n10 - num
		n12 - num
		n13 - num
		n14 - num
		n15 - num
	)
  (:init
		(empty t1)
		(empty t2)
		(fit-n-sum  n00  n03  n03)
		(fit-n-sum  n00  n07  n07)
		(fit-n-sum  n03  n03  n06)
		(fit-n-sum  n03  n07  n10)
		(fit-n-sum  n06  n03  n09)
		(fit-n-sum  n06  n07  n13)
		(fit-n-sum  n07  n03  n10)
		(fit-n-sum  n07  n07  n14)
		(fit-n-sum  n09  n03  n12)
		(fit-n-sum  n10  n03  n13)
		(fit-n-sum  n12  n03  n15)
		(= (total-cost) 0)
		(on-rack noner part3)
		(on-rack noner part4)
		(on-rack noner part5)
		(on-rack noner part1)
		(on-rack noner part2)
		(ready-to-unload part3)
		(next-to-unload part3 part4)
		(next-to-unload part4 part5)
		(next-to-unload part5 part1)
		(next-to-unload part1 part2)
		(next-to-unload part2 nonep)
		(no-rack-succ part1)
		(no-rack-pre part1)
		(no-rack-succ part2)
		(no-rack-pre part2)
		(no-rack-succ part3)
		(no-rack-pre part3)
		(no-rack-succ part4)
		(no-rack-pre part4)
		(no-rack-succ part5)
		(no-rack-pre part5)
		(size part1 n07)
		(size part2 n07)
		(size part3 n07)
		(size part4 n03)
		(size part5 n07)
		(level rack1 n00)
		(level rack2 n00)
		(unused rack1)
		(unused rack2)
		(needed-next nonep)
		(p-line-next plA part5)
		(p-line-succ part5 part3)
		(p-line-succ part3 part1)
		(p-line-succ part1 part4)
		(p-line-succ part4 part2)
		(p-line-succ part2 nonep)
		(p-line-succ nonep nonep)
	)
  (:goal (and 
		(processed part1)
		(processed part2)
		(processed part3)
		(processed part4)
		(processed part5)
	))
  (:metric minimize (total-cost))
)