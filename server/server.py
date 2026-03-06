import os, socket, time, pickle, warnings
from _thread import start_new_thread
warnings.filterwarnings("ignore")
from sklearn.feature_extraction.text import TfidfVectorizer

HOST       = os.getenv("SERVER_HOST", "0.0.0.0")
PORT       = int(os.getenv("SERVER_PORT", "12345"))
MODELS_DIR = os.getenv("MODELS_DIR", "/app/models")
MODEL_PATH     = os.path.join(MODELS_DIR, "LinearSVC.pkl")
VOCAB_PATH     = os.path.join(MODELS_DIR, "tfidf_vector_vocabulary.pkl")
STOPWORDS_PATH = os.path.join(MODELS_DIR, "stopwords.txt")

print("[SafeChat] Loading ML model...", flush=True)
model = pickle.load(open(MODEL_PATH, "rb"))
with open(STOPWORDS_PATH) as fh:
    STOPWORDS = fh.read().split("\n")
VOCABULARY = pickle.load(open(VOCAB_PATH, "rb"))
print("[SafeChat] Model loaded successfully.", flush=True)


class SafeChatServer:
    def __init__(self):
        self.rooms = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.sock.bind((HOST, PORT))
        self.sock.listen(100)
        print(f"[SafeChat] Server listening on {HOST}:{PORT}", flush=True)
        while True:
            conn, addr = self.sock.accept()
            print(f"[SafeChat] {addr[0]}:{addr[1]} connected", flush=True)
            start_new_thread(self._handle_client, (conn,))

    def _handle_client(self, conn):
        try:
            user_id = conn.recv(1024).decode().strip()
            room_id = conn.recv(1024).decode().strip()
            if room_id not in self.rooms:
                self.rooms[room_id] = []
                conn.send("New Group created".encode())
            else:
                conn.send("Welcome to chat room".encode())
            self.rooms[room_id].append(conn)
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        self._remove(conn, room_id); break
                    text = data.decode()
                    if text == "FILE":
                        self._relay_file(conn, room_id, user_id)
                    else:
                        is_bullying = self._classify(text)
                        self._broadcast(f"<{user_id}> {text}", conn, room_id, is_bullying)
                except (BrokenPipeError, ConnectionResetError) as e:
                    print(f"[SafeChat] Connection error: {e}", flush=True)
                    self._remove(conn, room_id); break
                except Exception as e:
                    print(f"[SafeChat] Error: {e!r}", flush=True); break
        finally:
            conn.close()

    def _classify(self, text):
        try:
            vec = TfidfVectorizer(stop_words=STOPWORDS, lowercase=True, vocabulary=VOCABULARY)
            pred = model.predict(vec.fit_transform([text]))
            is_bullying = int(pred[0]) != 0
            print(f"[SafeChat] [{'BULLYING' if is_bullying else 'OK'}] {text[:80]}", flush=True)
            return is_bullying
        except Exception as e:
            print(f"[SafeChat] Classification error: {e}", flush=True)
            return False

    def _broadcast(self, message, sender, room_id, is_bullying):
        payload = "[SafeChat] A message was hidden — bullying detected." if is_bullying else message
        for client in list(self.rooms.get(room_id, [])):
            if client != sender:
                try:
                    client.send(payload.encode())
                except Exception:
                    client.close(); self._remove(client, room_id)

    def _relay_file(self, sender, room_id, user_id):
        file_name = sender.recv(1024).decode()
        file_size = sender.recv(1024).decode()
        for client in list(self.rooms.get(room_id, [])):
            if client != sender:
                try:
                    client.send("FILE".encode()); time.sleep(0.05)
                    client.send(file_name.encode()); time.sleep(0.05)
                    client.send(file_size.encode()); time.sleep(0.05)
                    client.send(user_id.encode()); time.sleep(0.05)
                except Exception:
                    client.close(); self._remove(client, room_id)
        received = 0
        while str(received) != file_size:
            chunk = sender.recv(1024)
            received += len(chunk)
            for client in list(self.rooms.get(room_id, [])):
                if client != sender:
                    try:
                        client.send(chunk)
                    except Exception:
                        client.close(); self._remove(client, room_id)

    def _remove(self, conn, room_id):
        room = self.rooms.get(room_id, [])
        if conn in room:
            room.remove(conn)
        try:
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    SafeChatServer().start()
