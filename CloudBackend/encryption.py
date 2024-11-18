from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import base64

def encrypt_with_public_key(public_key_pem: str, plaintext: str) -> str:
   
    public_key_decode = base64.b64decode(public_key_pem)

    
    public_key = serialization.load_pem_public_key(public_key_decode)

    
    encrypted_data = public_key.encrypt(
        plaintext.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    
    return base64.b64encode(encrypted_data).decode('utf-8')

# Test
if __name__ == "__main__":
    val = encrypt_with_public_key("LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF5U0RROFV4SFUzWlMvOVpDNTNUTgpDQ1F1RjJXTWZ0Yk9QcTgrcklwQVVVaDFwTGNheHpxcmN2Umg1SjVDLzFTR2g0b3p6WE0xbXlmRkc0OFZ1ZjdJClR4MXNLVDVDM2ZlZUdSWVd2Q05MTnNRekhXVDNWR1JDSEJRemxQTnNPbUkxRnlpTWI0ODZJM2hoaFNjckpXMk4KR0s3TXcvT1RrWUMvQkh1VkI1cHJzRGljdjVrWVg4VDZ1TUZsblVtYjl5aTdlWUY5cUF1WGVReVNEU3B3dWtIago5dlNaSEZEV2w2RjE2MTNQUk1CYWFSbjZ1eG40S2NOMEowVisyTy9nMDRLNXl4enhxajVacmV6Qi9LVjd6WW5wCjNrZ2dqVmdaN2NFR3l6NUd6Z2hpRGZrRlBMUW5YdEgyNm5QZnIvTEFvcTNBUjlvRjcrUnZ4V2d5ZDFzVU5CUlcKcHdJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg==", "4242424")
    
    print(val)
