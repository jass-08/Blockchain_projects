import hashlib

# genesis, with difficulty of 5
m = hashlib.sha256()
# Who
m.update('Rob!'.encode())
# messages
m.update('Rob wuz here'.encode())
# timestamp
ts = 1651786804
m.update(ts.to_bytes(8, 'big'))
# nonce
m.update('4966792918599'.encode())

# Should match
print('637161f72e3db58310a048a3f2c3752df42f4409ccf30c257cb832ad9f800000')
print(m.hexdigest())

#next block
m = hashlib.sha256()
# previous hash
m.update('637161f72e3db58310a048a3f2c3752df42f4409ccf30c257cb832ad9f800000'.encode())
# who
m.update('Rob!'.encode())
# messages
m.update('test block'.encode())
# timestamp
ts = 1651786809
m.update(ts.to_bytes(8, 'big'))
# nonce
m.update('3464740178347'.encode())

# should match
print('d50309b0dcbcc0be66a733c602e48b2a3285e38af29b787cb8543ac2eb800000')
print(m.hexdigest())
