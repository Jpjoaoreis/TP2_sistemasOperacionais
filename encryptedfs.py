import os
import errno
from fuse import FUSE, Operations
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# Diretório real onde os arquivos criptografados ficam armazenados
REAL_PATH = './data'

# Chave e IV fixos para AES-128 em modo CBC
KEY = b'1234567890abcdef'  # 16 bytes (128 bits)
IV = b'abcdef1234567890'   # 16 bytes

# Gera o caminho completo do arquivo
def full_path(path):
    return os.path.join(REAL_PATH, path.lstrip('/'))

# Classe que implementa o sistema de arquivos criptografado
class EncryptedFS(Operations):

    # Retorna atributos de um arquivo (permissões, tamanho, etc.)
    def getattr(self, path, fh=None):
        full = full_path(path)
        if not os.path.exists(full):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        st = os.lstat(full)
        return dict((key, getattr(st, key)) for key in (
            'st_atime', 'st_ctime', 'st_gid', 'st_mode',
            'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    # Lista os arquivos de um diretório
    def readdir(self, path, fh):
        return ['.', '..'] + os.listdir(full_path(path))

    # Leitura de arquivos (dados são descriptografados)
    def read(self, path, size, offset, fh):
        with open(full_path(path), 'rb') as f:
            encrypted = f.read()
        decrypted = self.decrypt(encrypted)  # Descriptografa o conteúdo
        return decrypted[offset:offset + size]

    # Escrita em arquivos (dados são criptografados antes de salvar)
    def write(self, path, data, offset, fh):
        full = full_path(path)
        if os.path.exists(full):
            with open(full, 'rb') as f:
                encrypted = f.read()
            try:
                decrypted = self.decrypt(encrypted)
            except Exception:
                decrypted = b''  # Se falhar na descriptografia, assume vazio
        else:
            decrypted = b''

        # Atualiza o conteúdo na posição indicada
        content = decrypted[:offset] + data + decrypted[offset + len(data):]
        encrypted = self.encrypt(content)  # Criptografa novamente

        with open(full, 'wb') as f:
            f.write(encrypted)
        return len(data)

    # Criação de um arquivo vazio
    def create(self, path, mode):
        open(full_path(path), 'wb').close()
        return 0

    # Exclusão de arquivo
    def unlink(self, path):
        os.unlink(full_path(path))

    # Função de criptografia (AES-CBC + padding PKCS7)
    def encrypt(self, plaintext):
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(padded_data) + encryptor.finalize()

    # Função de descriptografia (AES-CBC + remoção de padding)
    def decrypt(self, ciphertext):
        cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(decrypted) + unpadder.finalize()

# Executa o sistema de arquivos
if __name__ == '__main__':
    os.makedirs(REAL_PATH, exist_ok=True)  # Cria o diretório de dados se não existir
    os.makedirs('./mnt', exist_ok=True)    # Cria o ponto de montagem
    FUSE(EncryptedFS(), './mnt', foreground=True)  # Monta o FS criptografado em ./mnt
