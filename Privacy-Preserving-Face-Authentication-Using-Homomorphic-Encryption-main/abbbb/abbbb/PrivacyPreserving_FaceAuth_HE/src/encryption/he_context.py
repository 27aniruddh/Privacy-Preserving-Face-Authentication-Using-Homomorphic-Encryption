"""Homomorphic Encryption context using TenSEAL"""

def create_he_context():
    """Create and return HE context"""
    try:
        import tenseal as ts
        context = ts.context(ts.SCHEME_TYPE.CKKS, 8192, coeff_mod_bit_sizes=[60, 40, 40, 60])
        context.global_scale = 2 ** 40
        context.generate_galois_keys()
        return context
    except Exception as e:
        print(f"Warning: Could not create HE context: {e}")
        return None
