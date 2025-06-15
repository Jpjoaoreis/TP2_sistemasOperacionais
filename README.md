# EncryptedFS - Sistema de Arquivos Criptografado com FUSE

Este projeto consiste na implementação de um sistema de arquivos virtual utilizando o FUSE (Filesystem in Userspace) com a linguagem Python, por meio da biblioteca `fusepy`. O objetivo principal é oferecer criptografia transparente de arquivos, assegurando a confidencialidade dos dados sem alterar a forma como os usuários interagem com o sistema.

## Funcionalidade

- Armazenamento criptografado dos arquivos no diretório real (`./data`)
- Acesso transparente a arquivos descriptografados via ponto de montagem (`./mnt`)
- Utilização do algoritmo AES em modo CBC com preenchimento PKCS7
- Chave e vetor de inicialização (IV) fixos para fins didáticos

## Estrutura do Projeto

```
encryptedfs_project/
├── encryptedfs.py        # Código principal do sistema de arquivos
├── data/                 # Diretório real de armazenamento (criptografado)
├── mnt/                  # Ponto de montagem (acesso transparente)
```

## Requisitos

- Sistema operacional baseado em Linux com suporte ao FUSE (recomenda-se Ubuntu)
- Python 3.6 ou superior
- Bibliotecas:
  - `fusepy`
  - `cryptography`

### Instalação das Dependências

```bash
sudo apt update
sudo apt install python3-pip fuse
pip3 install fusepy cryptography
```

## Execução

1. Extraia ou clone o repositório
2. Execute o script principal:

```bash
python3 encryptedfs.py
```

O sistema será montado no diretório `./mnt`. Deixe o processo em execução.

3. Em outro terminal, realize os testes:

```bash
echo "texto de teste" > ./mnt/arquivo.txt
cat ./mnt/arquivo.txt
ls ./data
cat ./data/arquivo.txt
```

4. Para desmontar o sistema:

```bash
fusermount -u ./mnt
```


