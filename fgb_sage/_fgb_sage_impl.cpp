#define USE_MY_OWN_IO 0

extern "C" {
#include "call_fgb.h"
}

#if LIBMODE == 1
int FGb_verb_info=0;
#endif

void init_fgb_gmp() {
    FGB(saveptr)();
}

void set_elim_order(UI32 bl1, UI32 bl2, char** liste) {
    FGB(PowerSet)(bl1, bl2, liste);
}

Dpol create_poly(UI32 n) {
    return FGB(creat_poly)(n);
}

void set_expos2(Dpol p, UI32 i0, I32* e, const UI32 nb) {
    FGB(set_expos2)(p, i0, e, nb);
}

void full_sort_poly2(Dpol p) {
    FGB(full_sort_poly2)(p);
}

const int fgb_mac_max_input = FGB_MAC_MAX_INPUT;

UI32 fgb(Dpol* p, UI32 np, Dpol* q, UI32 nq, double* t0, FGB_Options options) {
#if FGB_MAC
    // Apparently, on Mac OS, there is a strange bug causing FGB to return
    // false results (way too few polynomials in output, e.g. for Cyclic ideals
    // 4 and 5), unless at least one of p and q is allocated on the stack, and
    // the options need to be created here as well.
    Dpol p2[FGB_MAC_MAX_INPUT];
    SFGB_Options opts;
    UI32 i;

    FGb_set_default_options(&opts);
    opts._env._force_elim = options->_env._force_elim;
    opts._env._index = options->_env._index;
    opts._verb = options->_verb;
    for (i = 0; i < np; i++) {
        p2[i] = p[i];
    }
    return FGB(fgb)(p2, np, q, nq, t0, &opts);
#else
    return FGB(fgb)(p, np, q, nq, t0, options);
#endif
}

UI32 nb_terms(Dpol p) {
    return FGB(nb_terms)(p);
}

void reset_memory() {
    FGB(reset_memory)();
}

void restoreptr() {
    FGB(restoreptr)();
}

I32 fgb_internal_version() {
    return FGB(internal_version)();
}
