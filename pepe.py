b"\x50"
print(b"\x50")


print(b"hola")
print(b'mundo')

print(b'holamundo')

s = "Holamundkkkk"
binary = ' '.join(format(ord(c), '08b') for c in s)
print(binary)