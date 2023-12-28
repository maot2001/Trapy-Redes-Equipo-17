def join_byte_arrays(byte_arrays):
    # Aplanar la lista de listas en una sola lista
    flattened = [item for sublist in byte_arrays for item in sublist]
    
    # Unir todos los arrays de bytes en uno solo
    return b''.join(flattened)
