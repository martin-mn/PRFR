# The two census programs: pairs (leading-order GTH, coefficients in double precision) and pairsq (the same, with every
# coefficient an exact rational).  Drop -march=native if your compiler rejects it; the results do not depend on it.
CC ?= cc
CFLAGS ?= -O3 -march=native

all: pairs pairsq

pairs: pairs.c
	$(CC) $(CFLAGS) -o pairs pairs.c

pairsq: pairsq.c
	$(CC) $(CFLAGS) -o pairsq pairsq.c

# the self-checks of the Cannon kit (cannon/compile.sh): 1e5 random pairs exact against double, and one pair
selftest: pairs pairsq
	./pairsq cmp 100000 7
	./pairsq pair 19079 65535

clean:
	rm -f pairs pairsq

.PHONY: all selftest clean
