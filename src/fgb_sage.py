from sage.rings.polynomial.multi_polynomial_sequence import PolynomialSequence

MAX_PRIME = 65521

def groebner_basis(polys, **kwds):
    r"""
    Compute a Groebner basis of an ideal using FGb.

    Supported term orders of the underlying polynomial ring are ``degrevlex``
    orders, as well as block orders with two ``degrevlex`` blocks (elimination
    orders).  Supported coefficient fields are QQ and finite prime fields of
    size up to ``MAX_PRIME`` = 65521 < 2^16.

    INPUT:

    - ``polys`` -- an ideal or a polynomial sequence, the generators of an
      ideal.

    - ``threads`` -- integer (default: `1`); only seems to work in positive
      characteristic.

    - ``force_elim`` -- integer (default: `0`); if ``force_elim=1``, then the
      computation will return only the result of the elimination, if an
      elimination order is used.

    - ``verbosity`` -- integer (default: `1`), display progress info.

    - ``matrix_bound`` -- integer (default: `500000`); this is is the maximal
      size of the matrices generated by F4.  This value can be increased
      according to available memory.

    - ``max_base`` -- integer (default: `100000`); maximum number of
      polynomials in output.

    OUTPUT: the Groebner basis.

    EXAMPLES:

    This example computes a Groebner basis with respect to an elimination order::

        sage: R = PolynomialRing(QQ, 5, 'x', order="degrevlex(2),degrevlex(3)")
        sage: I = sage.rings.ideal.Cyclic(R)
        sage: import fgb_sage                               # optional fgb_sage
        sage: gb = fgb_sage.groebner_basis(I)               # optional fgb_sage, random
        ...
        sage: gb.is_groebner(), gb.ideal() == I             # optional fgb_sage
        (True, True)

    Over finite fields, parallel computations are supported::

        sage: R = PolynomialRing(GF(fgb_sage.MAX_PRIME), 4, 'x')      # optional fgb_sage
        sage: I = sage.rings.ideal.Katsura(R)                         # optional fgb_sage
        sage: gb = fgb_sage.groebner_basis(I, threads=2, verbosity=0) # optional fgb_sage, random
        sage: gb.is_groebner(), gb.ideal() == I                       # optional fgb_sage
        (True, True)

    If `fgb_sage.groebner_basis` is called with an ideal, the result is cached
    on `MPolynomialIdeal.groebner_basis` so that other computations on the
    ideal do not need to recompute a Groebner basis::

        sage: I.groebner_basis.is_in_cache()            # optional fgb_sage
        True
        sage: I.groebner_basis() is gb                  # optional fgb_sage
        True

    However, note that `gb.ideal()` returns a new ideal and, thus, does not
    have a Groebner basis in cache::

        sage: gb.ideal().groebner_basis.is_in_cache()   # optional fgb_sage
        False

    TESTS:

        sage: R = PolynomialRing(QQ, 5, 'x', order="degrevlex(2),degrevlex(3)")
        sage: I = sage.rings.ideal.Cyclic(R)
        sage: import fgb_sage
        sage: gb = fgb_sage.groebner_basis(I, force_elim=1) # optional fgb_sage, random
        ...
        sage: I.groebner_basis.is_in_cache()                # optional fgb_sage
        False
    """
    kwds.setdefault('force_elim', 0)
    kwds.setdefault('threads', 1)
    kwds.setdefault('matrix_bound', 500000)
    kwds.setdefault('verbosity', 1)
    kwds.setdefault('max_base', 100000)

    polyseq = PolynomialSequence(polys)
    ring = polyseq.ring()
    field = ring.base_ring()
    if not field.is_prime_field():
        raise NotImplementedError("base ring must be QQ or finite prime field")
    if field.characteristic() > MAX_PRIME:
        raise NotImplementedError("maximum prime field size is %s" % MAX_PRIME)
    blocks = ring.term_order().blocks()
    if not (len(blocks) <= 2 and all(order.name() == 'degrevlex' for order in blocks)):
        raise NotImplementedError("term order must be Degree-Reverse-Lexicographic block order with at most 2 blocks")
    n_elim_variables = len(blocks[0])

    gb = None
    if field.characteristic() == 0:
        import _fgb_sage_int
        gb = _fgb_sage_int.fgb_eliminate(polyseq, n_elim_variables, **kwds)
    else:
        import _fgb_sage_modp
        gb = _fgb_sage_modp.fgb_eliminate(polyseq, n_elim_variables, **kwds)

    from sage.rings.polynomial.multi_polynomial_ideal import MPolynomialIdeal
    if isinstance(polys, MPolynomialIdeal) and not kwds['force_elim']:
        if not polys.groebner_basis.is_in_cache():
            polys.groebner_basis.set_cache(gb)

    return gb

def eliminate(polys, elim_variables, **kwds):
    r"""
    Compute a Groebner basis with respect to an elimination order defined by
    the given variables.

    INPUT:

    - ``polys`` -- an ideal or a polynomial sequence.

    - ``elim_variables`` -- the variables to eliminate.

    - ``force_elim`` -- integer (default: `1`).

    - ``kwds`` -- same as in :func:`groebner_basis`.

    OUTPUT: a Groebner basis of the elimination ideal.

    EXAMPLES:

        sage: R.<x,y,t,s,z> = PolynomialRing(QQ,5)
        sage: I = R * [x-t,y-t^2,z-t^3,s-x+y^3]
        sage: import fgb_sage                                # optional - fgb_sage
        sage: gb = fgb_sage.eliminate(I, [t,s], verbosity=0) # optional - fgb_sage, random
        open simulation
        sage: gb                                             # optional - fgb_sage
        [x^2 - y, x*y - z, y^2 - x*z]
        sage: gb.is_groebner()                               # optional - fgb_sage
        True
        sage: gb.ideal() == I.elimination_ideal([t,s])       # optional - fgb_sage
        True

    .. SEEALSO::

        :func:`groebner_basis`

    .. WARNING::

        In some cases, this function fails to set the correct elimination order, see :trac:`24981`.
    """
    kwds.setdefault('force_elim', 1)
    polyseq = PolynomialSequence(polys)
    ring = polyseq.ring()
    elim_variables = set(elim_variables)
    block1 = [x for x in ring.gens() if x in elim_variables]
    block2 = [x for x in ring.gens() if x not in elim_variables]
    from sage.rings.polynomial.term_order import TermOrder
    if len(block1) == 0 or len(block2) == 0:
        t = TermOrder("degrevlex", ring.ngens())
    else:
        t = TermOrder("degrevlex", len(block1)) + TermOrder("degrevlex", len(block2))
    if t == ring.term_order() and set(ring.gens()[:len(block1)]) == elim_variables:
        return groebner_basis(polyseq, **kwds)
    else:
        block_ring = ring.change_ring(names=block1+block2, order=t)
        gb = groebner_basis(PolynomialSequence(block_ring, polyseq), **kwds)
        return PolynomialSequence(ring, gb, immutable=True)

"""
    Get the internal version of FGb.

    OUTPUT: a dictionary containing the versions of FGb for `FGb_int` and
    `FGb_modp`, characteristic 0 and positive characteristic, respectively.
    These versions differ between Linux and Mac.

    EXAMPLES:

        sage: import fgb_sage                   # optional - fgb_sage
        sage: fgb_sage.internal_version()       # optional - fgb_sage, random
        {'FGb_int': 14537, 'FGb_modp': 14536}
"""
def internal_version():
    import _fgb_sage_int, _fgb_sage_modp
    return dict(FGb_int=_fgb_sage_int.internal_version(),
            FGb_modp=_fgb_sage_modp.internal_version())
