ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
M = 26

def clean_text(s):
    # Uppercase and keep letters only.
    return "".join(ch for ch in s.upper() if ch.isalpha())


def letter_to_number(ch):
    return ord(ch) - ord('A')


def number_to_letter(n):
    return chr((n % M) + ord('A'))

def pad_text(s, block_size = 2, pad_char= 'X'):
    s = clean_text(s)
    if len(s) % block_size != 0:
        s += pad_char * (block_size - (len(s) % block_size))
    return s

def egcd(a, b):
    # Extended Euclidean algorithm -> (g, x, y) with a*x + b*y = g = gcd(a,b).
    # For finding 
    if a == 0:
        return (b, 0, 1)
    else:
        g, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return (g, x, y)
    
def modinv(a,m):
    #Return modular inverse of a mod m, or raise error if it doesn't exist.
    
    g,x,_ = egcd(a%m, m)
    if g!=1:
        raise ValueError(f"No modular inverse for {a} modulo {m}")
    return x % m


def det(mat):
    a,b,c,d = mat
    return (a*d - b*c) % M

def is_invertible(mat):
    return egcd(det(mat), M)[0] == 1

def invert_matrix_2x2(mat):
    a, b, c, d = mat
    det = (a * d - b * c) % M
    if egcd(det, M)[0] != 1:
        raise ValueError("Matrix not invertible modulo {}".format(M))
    det_inv = modinv(det, M)
    # adjugate * det_inv mod M
    inv = ((d * det_inv) % M,
           ((-b) * det_inv) % M,
           ((-c) * det_inv) % M,
           (a * det_inv) % M)
    return inv

def mat_vec_mult(mat, vec):
    a, b, c, d = mat
    x, y = vec
    return [ (a*x + b*y) % M, (c*x + d*y) % M ]

def encrypt(plaintext, key_mat):
    pt = pad_text(plaintext, 2)
    nums = [letter_to_number(ch) for ch in pt]
    out = []
    for i in range(0, len(nums), 2):
        vec = (nums[i], nums[i+1])
        res = mat_vec_mult(key_mat, vec)
        out.extend(res)
    return ''.join(number_to_letter(n) for n in out)

def decrypt(ciphertext: str, key_mat) -> str:
    ct = pad_text(ciphertext, 2)
    nums = [letter_to_number(ch) for ch in ct]
    try:
        inv = invert_matrix_2x2(key_mat)
    except ValueError:
        # not invertible
        return None
    out = []
    for i in range(0, len(nums), 2):
        vec = (nums[i], nums[i+1])
        res = mat_vec_mult(inv, vec)
        out.extend(res)
    return ''.join(number_to_letter(n) for n in out)

# -- scoring and brute-force ------------------------------------------------
COMMON_WORDS = ["THE", "AND", "TO", "OF", "IS", "IN", "IT", "YOU", "FOR", "THAT"]

def english_score(s: str) -> int:
    """Simple heuristic scoring. Higher = more likely English plaintext."""
    s = s.upper()
    score = 0
    # reward common words
    for w in COMMON_WORDS:
        score += 10 * s.count(w)
    # reward vowels (rough)
    vowels = sum(s.count(v) for v in "AEIOU")
    score += vowels
    # reward common digrams
    for dg in ["TH","HE","IN","ER","AN","RE","ON","AT","EN","ED"]:
        score += 2 * s.count(dg)
    return score


def brute_force(ciphertext: str, top_n: int = 10, known_plain_substring: str = None):
    """Try all invertible 2x2 keys. Return top_n results sorted by score.
       If known_plain_substring is provided, print matches that contain it (fast check).
    """
    ct = pad_text(ciphertext, 2)
    candidates = []
    # iterate all 26^4 possible 2x2 matrices
    for a in range(M):
        for b in range(M):
            for c in range(M):
                for d in range(M):
                    key = (a,b,c,d)
                    # require invertible matrix mod 26
                    if not is_invertible(key):
                        continue
                    # decrypt using this key
                    pt = decrypt(ct, key)
                    if pt is None:
                        continue
                    # optional quick filter: if user provided known substring and it's present -> record & maybe stop early
                    if known_plain_substring:
                        if known_plain_substring.upper() in pt:
                            # immediate likely hit; return top few around it
                            return [(key, pt, english_score(pt))]
                        else:
                            continue
                    sc = english_score(pt)
                    # keep only candidates with nonzero score to reduce memory
                    if sc > 0:
                        candidates.append((key, pt, sc))
    # sort by score desc
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates[:top_n]


# -- user interaction -------------------------------------------------------
def parse_key_from_input(s: str):
    """Parse 4 integers from a space/comma separated string into a 2x2 key tuple (row-major)."""
    parts = [p.strip() for p in s.replace(',', ' ').split()]
    if len(parts) != 4:
        raise ValueError("Provide exactly 4 integers for a 2x2 key (row-major).")
    nums = [int(x) % M for x in parts]
    return (nums[0], nums[1], nums[2], nums[3])


def pretty_key(k):
    a,b,c,d = k
    return f"[[{a:2d}, {b:2d}], [{c:2d}, {d:2d}]]"


def main():
    print("2x2 Hill Cipher (Brute-force mode available)")
    while True:
        print("\nMenu:")
        print("1. Encrypt (provide key)")
        print("2. Brute-force decrypt ciphertext (try all invertible 2x2 keys)")
        print("3. Exit")
        choice = input("Choice: ").strip()
        if choice == "1":
            try:
                key_input = input("Enter 4 integers for key (row-major), e.g. '3 3 2 5': ")
                key = parse_key_from_input(key_input)
                if not is_invertible(key):
                    print("Warning: provided key is NOT invertible modulo 26 and cannot be used for decryption.")
                plain = input("Enter plaintext (letters only): ")
                encrypted = encrypt(plain, key)
                print("Ciphertext:", encrypted)
            except Exception as e:
                print("Error:", e)
        elif choice == "2":
            ct = input("Enter ciphertext (letters only): ").strip()
            if not ct.isalpha():
                print("Ciphertext must be alphabetic only.")
                continue
            known = input("Optional known plaintext substring (press Enter to skip): ").strip()
            if known == "":
                known = None
            print("Brute-forcing... (this may take a little while)")
            results = brute_force(ct, top_n=20, known_plain_substring=known)
            if not results:
                print("No high-scoring candidates found (or none matched the known substring).")
            else:
                # results may be single tuple when known substring matched returned early
                if isinstance(results[0], tuple) and len(results) == 3 and isinstance(results[2], int):
                    # single returned match
                    k, pt, sc = results[0]
                    print(f"Match found: key {pretty_key(k)} -> plaintext: {pt} (score {sc})")
                else:
                    print(f"Top {len(results)} candidates:")
                    for idx, (k, pt, sc) in enumerate(results, start=1):
                        print(f"{idx:2d}. key {pretty_key(k)} -> {pt} (score {sc})")
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
        main()
