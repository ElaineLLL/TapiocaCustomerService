import secrets
import jwt
import datetime
# Generate a random secret key
secret_key = secrets.token_urlsafe(32)

def encode_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    secret_key = 'sGDqQuDiiCmKrewhyA2CTF3YqXE9-1Ukv7CHTsAgLQY'
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def decode_token(token):
    secret_key = 'sGDqQuDiiCmKrewhyA2CTF3YqXE9-1Ukv7CHTsAgLQY'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

# Example usage
user_id = '123'
encoded_token = encode_token(user_id)
decoded_token = decode_token(encoded_token)

print(f'Encoded Token: {encoded_token}')
print(f'Decoded Token: {decoded_token}')
