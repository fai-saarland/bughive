(define
	(problem test)
	(:domain beluga)
  (:objects
		t1 - beluga-truck
		t2 - fab-truck
		rack1 - rack
		rack2 - rack
		rack3 - rack
		part1 - part
		part2 - part
		part3 - part
		part4 - part
		part5 - part
		part6 - part
		plA - production-line
		n03 - num
		n05 - num
		n06 - num
		n08 - num
		n09 - num
		n10 - num
		n11 - num
		n12 - num
		n13 - num
		n14 - num
		n15 - num
	)
  (:init
		(empty t1)
		(empty t2)
		(fit-n-sum  n00  n03  n03)
		(fit-n-sum  n00  n05  n05)
		(fit-n-sum  n00  n06  n06)
		(fit-n-sum  n03  n03  n06)
		(fit-n-sum  n03  n05  n08)
		(fit-n-sum  n03  n06  n09)
		(fit-n-sum  n05  n03  n08)
		(fit-n-sum  n05  n05  n10)
		(fit-n-sum  n05  n06  n11)
		(fit-n-sum  n06  n03  n09)
		(fit-n-sum  n06  n05  n11)
		(fit-n-sum  n06  n06  n12)
		(fit-n-sum  n08  n03  n11)
		(fit-n-sum  n08  n05  n13)
		(fit-n-sum  n08  n06  n14)
		(fit-n-sum  n09  n03  n12)
		(fit-n-sum  n09  n05  n14)
		(fit-n-sum  n09  n06  n15)
		(fit-n-sum  n10  n03  n13)
		(fit-n-sum  n10  n05  n15)
		(fit-n-sum  n11  n03  n14)
		(fit-n-sum  n12  n03  n15)
		(= (total-cost) 0)
		(on-rack noner part4)
		(on-rack noner part1)
		(on-rack noner part2)
		(on-rack noner part6)
		(on-rack noner part5)
		(on-rack noner part3)
		(ready-to-unload part4)
		(next-to-unload part4 part1)
		(next-to-unload part1 part2)
		(next-to-unload part2 part6)
		(next-to-unload part6 part5)
		(next-to-unload part5 part3)
		(next-to-unload part3 nonep)
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
		(no-rack-succ part6)
		(no-rack-pre part6)
		(size part1 n06)
		(size part2 n03)
		(size part3 n06)
		(size part4 n05)
		(size part5 n06)
		(size part6 n05)
		(level rack1 n00)
		(level rack2 n00)
		(level rack3 n00)
		(unused rack1)
		(unused rack2)
		(unused rack3)
		(needed-next nonep)
		(p-line-next plA part2)
		(p-line-succ part2 part6)
		(p-line-succ part6 part4)
		(p-line-succ part4 part3)
		(p-line-succ part3 part1)
		(p-line-succ part1 part5)
		(p-line-succ part5 nonep)
		(p-line-succ nonep nonep)
	)
  (:goal (and 
		(processed part1)
		(processed part2)
		(processed part3)
		(processed part4)
		(processed part5)
		(processed part6)
	))
  (:metric minimize (total-cost))
)