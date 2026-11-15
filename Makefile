hw  := 30
swd := .8
all: six eight

six: sixfp2 sixfp3 sixspn sixspe sixfhni sixshni sixfhei sixshei sixfhno sixfheo
eight: eightfp2 eightfp3 eightspn eightfoi eightsoni eightsoei eightsono eightsoeo
sixfp2:
	python six.py $@ $(hw) $(swd)
sixfp3:
	python six.py $@ $(hw) $(swd) fill petals 3
sixspn:
	python six.py $@ $(hw) $(swd) stroke
sixspe:
	python six.py $@ $(hw) $(swd) stroke petals E
sixfhni:
	python six.py $@ $(hw) $(swd) fill hexagon
sixshni:
	python six.py $@ $(hw) $(swd) stroke hexagon
sixfhei:
	python six.py $@ $(hw) $(swd) fill hexagon E
sixshei:
	python six.py $@ $(hw) $(swd) stroke hexagon E
sixfhno:
	python six.py $@ $(hw) $(swd) fill hexagon N outer
sixfheo:
	python six.py $@ $(hw) $(swd) fill hexagon E outer
eightfp2: 
	python eight.py $@ $(hw) $(swd)
eightfp3:
	python eight.py $@ $(hw) $(swd) fill petals 3
eightspn:
	python eight.py $@ $(hw) $(swd) stroke
eightfoi:
	python eight.py $@ $(hw) $(swd) fill octagon
eightsoni:
	python eight.py $@ $(hw) $(swd) stroke octagon
eightsoei:
	python eight.py $@ $(hw) $(swd) stroke octagon E
eightsono:
	python eight.py $@ $(hw) $(swd) stroke octagon E outer
eightsoeo:
	python eight.py $@ $(hw) $(swd) stroke octagon N outer
