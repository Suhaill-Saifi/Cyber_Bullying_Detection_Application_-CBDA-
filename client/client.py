import os, sys, select, time, pickle, warnings, socket
warnings.filterwarnings("ignore")
from sklearn.feature_extraction.text import TfidfVectorizer

SERVER_HOST    = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT    = int(os.getenv("SERVER_PORT", "12345"))
MODELS_DIR     = os.getenv("MODELS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
MODEL_PATH     = os.path.join(MODELS_DIR, "LinearSVC.pkl")
VOCAB_PATH     = os.path.join(MODELS_DIR, "tfidf_vector_vocabulary.pkl")
STOPWORDS_PATH = os.path.join(MODELS_DIR, "stopwords.txt")

model      = pickle.load(open(MODEL_PATH, "rb"))
vocabulary = pickle.load(open(VOCAB_PATH, "rb"))
with open(STOPWORDS_PATH) as fh:
    stopwords = fh.read().split("\n")

def classify(text):
    vec = TfidfVectorizer(stop_words=stopwords, lowercase=True, vocabulary=vocabulary)
    return int(model.predict(vec.fit_transform([text]))[0]) != 0

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.connect((SERVER_HOST, SERVER_PORT))
print("Connected to SafeChat server.")
user_id = input("Username : ").strip()
room_id  = input("Room ID  : ").strip()
srv.send(user_id.encode()); time.sleep(0.1)
srv.send(room_id.encode())

while True:
    readable, _, _ = select.select([sys.stdin, srv], [], [])
    for sock in readable:
        if sock is srv:
            print(sock.recv(1024).decode())
        else:
            text = sys.stdin.readline().strip()
            if not text:
                continue
            if text.upper() == "FILE":
                path = input("File path: ").strip()
                size = str(os.path.getsize(path))
                srv.send("FILE".encode()); time.sleep(0.1)
                srv.send(("client_" + os.path.basename(path)).encode()); time.sleep(0.1)
                srv.send(size.encode()); time.sleep(0.1)
                with open(path, "rb") as fh:
                    chunk = fh.read(1024)
                    while chunk:
                        srv.send(chunk); chunk = fh.read(1024)
                print("<You> [File sent successfully]")
            else:
                if classify(text):
                    print("Your message was blocked — please communicate respectfully.")
                else:
                    srv.send(text.encode())
                    print("<You> " + text)
