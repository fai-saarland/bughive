

(define (problem mbw-b10-t3-s1498)
(:domain matching-bw-typed)
(:objects h1 h2 - hand b1 b2 b3 b4 b5 b6 b7 b8 b9 b10  - block)
(:init
 (empty h1)
 (empty h2)
 (hand-positive h1)
 (hand-negative h2)
 (solid b1)
 (block-positive b1)
 (on b1 b10)
 (solid b2)
 (block-positive b2)
 (on-table b2)
 (solid b3)
 (block-positive b3)
 (on b3 b7)
 (solid b4)
 (block-positive b4)
 (on b4 b2)
 (solid b5)
 (block-positive b5)
 (on b5 b8)
 (solid b6)
 (block-negative b6)
 (on b6 b4)
 (solid b7)
 (block-negative b7)
 (on-table b7)
 (solid b8)
 (block-negative b8)
 (on b8 b9)
 (solid b9)
 (block-negative b9)
 (on-table b9)
 (solid b10)
 (block-negative b10)
 (on b10 b5)
 (clear b1)
 (clear b3)
 (clear b6)
)
(:goal
(and
 (on b1 b2)
 (on b3 b7)
 (on b4 b10)
 (on b5 b8)
 (on b6 b4)
 (on b9 b5)
 (on b10 b1))
)
)


