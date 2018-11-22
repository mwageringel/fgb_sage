# distutils: language = c++

# _fgb_int.pyx is source file,
# _fgb_modp.pyx is auto-generated!
from sage.libs.gmp.types cimport mpz_t, mpz_ptr
from sage.libs.gmp.mpz cimport mpz_init_set_si
from sage.rings.integer cimport Integer
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cysignals.signals cimport sig_on, sig_off, sig_check

from sage.libs.singular.decl cimport (
        ring, poly, n_Init, p_ISet, p_Init, p_SetCoeff, nlInit2gmp, n_Init,
        p_SetExp, p_Setm, p_Add_q )
from sage.rings.polynomial.multi_polynomial_libsingular cimport (
        new_MP, MPolynomial_libsingular, MPolynomialRing_libsingular )
from sage.libs.singular.singular cimport overflow_check

cdef extern from "_fgb_sage_impl.cpp":
    # "style.h"
    ctypedef unsigned UI32
    ctypedef int I32
    ctypedef I32 Boolean

    # "call_fgb.h"
    ctypedef void* Dpol
    ctypedef Dpol Dpol_INT
    cdef void threads_FGb(int t)
    # fgb library functions with differing signatures
    IF PY_LIBMODE == 2:
        cdef extern void init_FGb_Integers()
        cdef extern void FGb_int_set_coeff_gmp(Dpol_INT p, UI32 i0, mpz_ptr x)
        cdef extern int FGb_int_export_poly_INT_gmp2(I32 n, I32 m, mpz_ptr* res, I32* E, Dpol_INT p)
    ELSE:
        cdef extern void init_FGb_Modp(const int p);
        cdef extern void FGb_set_coeff_I32(Dpol p, UI32 i0, I32 buf)
        cdef extern I32 FGb_export_poly(I32 n, I32 m, I32* E, I32* P, Dpol p)

    # "protocol_maple.h"
    ctypedef extern struct SFGB_Comp_Desc:
        I32 _force_elim
        UI32 _index
    ctypedef extern struct SFGB_Options:
        SFGB_Comp_Desc _env
        I32 _verb
    ctypedef extern SFGB_Options* FGB_Options
    cdef void FGb_set_default_options(FGB_Options options)

    # "_fgb_sage_impl.cpp"
    # fgb library functions with common signatures
    void init_fgb_gmp()
    Dpol create_poly(UI32 n)
    void set_elim_order(UI32 bl1, UI32 bl2, char** liste)
    void set_expos2(Dpol p, UI32 i0, I32* e, const UI32 nb)
    void full_sort_poly2(Dpol p)
    UI32 nb_terms(Dpol p)
    void reset_memory()
    void restoreptr()
    I32 fgb_internal_version()
    UI32 fgb(Dpol* p, UI32 np, Dpol* q, UI32 nq, double* t0, FGB_Options options) nogil
    IF PY_FGB_MAC:
        const int fgb_mac_max_input

def internal_version():
    return fgb_internal_version()

def fgb_eliminate(polyseq, n_elim_variables, **kwds):
    cdef SFGB_Options Opt
    cdef FGB_Options options = &Opt
    try:
        init_fgb_gmp() # First thing to do: GMP orignal memory allocators are saved
        IF PY_LIBMODE == 1:
            field = polyseq.ring().base_ring()
            init_FGb_Modp(field.characteristic())
        ELSE:
            init_FGb_Integers()

        threads_FGb(kwds['threads'])
        FGb_set_default_options(options)
        options._env._force_elim = kwds['force_elim']
        options._env._index = kwds['matrix_bound']
        options._verb = kwds['verbosity']
        # changes to the options need to be added to _fgb_sage_impl.c as well

        computation = FGbComputation(polyseq, n_elim_variables, kwds['max_base'])
        return computation.run(options)

    finally:
        reset_memory()
        restoreptr() # restore original GMP allocators

cdef void create_polys(object polys, I32* exponents, UI32 n_variables, Dpol* input_basis):
    cdef Dpol q
    cdef UI32 i, j, n_monoms
    for (k, (cs, es)) in enumerate(polys):
        n_monoms = len(cs)
        q = create_poly(n_monoms)
        for i in xrange(n_monoms):
            IF PY_LIBMODE == 2:
                FGb_int_set_coeff_gmp(q, i, (<Integer> cs[i]).value)
            ELSE:
                FGb_set_coeff_I32(q, i, cs[i])
        for i in xrange(n_monoms):
            for j in xrange(n_variables):
                exponents[j] = es[i][j]
            set_expos2(q, i, exponents, n_variables)
        full_sort_poly2(q)
        input_basis[k] = q

cdef class FGbComputation:
    cdef:
        Dpol* output_basis
        Dpol* input_basis
        char** variables
        I32* exponents
        UI32 n_variables
        int n_input, max_base
        object pystr_variables # to keep references alive
        double cputime
        MPolynomialRing_libsingular ring

    def __cinit__(self, object polyseq, int n_elim_variables, int max_base):
        from sage.rings.integer_ring import ZZ
        def int_coeffs(p):
            IF PY_LIBMODE == 2:
                d = p.denominator()
                return [ZZ(c*d) for c in p.coefficients()]
            ELSE:
                return [ZZ(c) for c in p.coefficients()]
        polys = ((int_coeffs(p), p.exponents()) for p in polyseq)

        self.n_input = len(polyseq)
        IF PY_FGB_MAC:
            if self.n_input > fgb_mac_max_input:
                raise ValueError("On Mac OS, the number of input polynomials is limited to %d." % fgb_mac_max_input)
        self.ring = <MPolynomialRing_libsingular> polyseq.ring()
        self.n_variables = self.ring.ngens()
        self.max_base = max_base
        self.output_basis = <Dpol*> PyMem_Malloc(self.max_base * sizeof(Dpol))
        self.input_basis = <Dpol*> PyMem_Malloc(self.n_input * sizeof(Dpol))
        self.variables = <char**> PyMem_Malloc(self.n_variables * sizeof(char*))
        self.exponents = <I32*> PyMem_Malloc(self.n_variables * sizeof(I32*))
        if not self.input_basis or not self.output_basis or not self.variables or not self.exponents:
            raise MemoryError()

        self.pystr_variables = [str(x) for x in self.ring.gens()]
        cdef int i, j, k
        for (i, x) in enumerate(self.pystr_variables):
            self.variables[i] = x
        set_elim_order(n_elim_variables, self.n_variables - n_elim_variables, self.variables)
        create_polys(polys, self.exponents, self.n_variables, self.input_basis)

    def __dealloc__(self):
        PyMem_Free(self.output_basis)
        PyMem_Free(self.input_basis)
        PyMem_Free(self.variables)
        PyMem_Free(self.exponents)

    cdef object run(self, FGB_Options options):
        cdef UI32 n_output
        sig_on()
        n_output = fgb(self.input_basis, self.n_input, self.output_basis, self.max_base, &self.cputime, options)
        sig_off()
        cdef int i
        from sage.rings.polynomial.multi_polynomial_sequence import PolynomialSequence
        return PolynomialSequence(self.ring,
                [PolyConversion(self, i).conv_poly(self.ring) for i in range(n_output)], # TODO iter bug :trac:`25989`.
                immutable=True)

cdef class PolyConversion:
    cdef UI32* monoms
    IF PY_LIBMODE == 2:
        cdef mpz_ptr* coeffs
    ELSE:
        cdef I32* coeffs
    cdef UI32 n_variables, n_monoms
    cdef Dpol q

    def __cinit__(self, FGbComputation comp, int q_idx):
        self.q = comp.output_basis[q_idx]
        self.n_monoms = nb_terms(self.q)
        self.n_variables = comp.n_variables
        self.monoms = <UI32*> PyMem_Malloc(self.n_monoms * self.n_variables * sizeof(UI32))
        IF PY_LIBMODE == 2:
            self.coeffs = <mpz_ptr*> PyMem_Malloc(self.n_monoms * sizeof(mpz_ptr))
        ELSE:
            self.coeffs = <I32*> PyMem_Malloc(self.n_monoms * sizeof(I32))
        if not self.monoms or not self.coeffs:
            raise MemoryError()

    def __dealloc__(self):
        PyMem_Free(self.monoms)
        PyMem_Free(self.coeffs)

    cdef MPolynomial_libsingular conv_poly(self, MPolynomialRing_libsingular mp_ring):
        sig_check()
        cdef UI32* e
        cdef UI32 j, k
        IF PY_LIBMODE == 2:
            FGb_int_export_poly_INT_gmp2(self.n_variables, self.n_monoms, self.coeffs, <I32*> self.monoms, self.q)
        ELSE:
            FGb_export_poly(self.n_variables, self.n_monoms, <I32*> self.monoms, self.coeffs, self.q)

        cdef ring* _ring
        cdef poly* _p
        cdef poly* mon
        IF PY_LIBMODE == 2:
            cdef mpz_t one
            mpz_init_set_si(one, 1)
        _ring = mp_ring._ring
        _p = p_ISet(0, _ring)
        for j in xrange(self.n_monoms):
            e = self.monoms + j * self.n_variables
            mon = p_Init(_ring)
            IF PY_LIBMODE == 2:
                p_SetCoeff(mon, nlInit2gmp(self.coeffs[j], one, _ring.cf), _ring)
            ELSE:
                p_SetCoeff(mon, n_Init(self.coeffs[j], _ring), _ring)
            for k in xrange(self.n_variables):
                overflow_check(e[k], _ring)
                p_SetExp(mon, k+1, e[k], _ring)
            p_Setm(mon, _ring)
            _p = p_Add_q(_p, mon, _ring)
        return new_MP(mp_ring, _p)
