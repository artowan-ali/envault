# envault

Encrypted local environment variable manager with team-sharing support via git-compatible diffs.

---

## Installation

```bash
pip install envault
```

Or with pipx for isolated installs:

```bash
pipx install envault
```

---

## Usage

Initialize a vault in your project directory:

```bash
envault init
```

Add and encrypt environment variables:

```bash
envault set DATABASE_URL "postgres://user:pass@localhost/mydb"
envault set API_KEY "sk-abc123"
```

Load variables into your shell session:

```bash
eval $(envault load)
```

Export a git-compatible diff to share changes with your team:

```bash
envault diff > changes.evault
envault apply changes.evault
```

View all stored keys (values remain encrypted):

```bash
envault list
```

---

## Team Sharing

Envault generates encrypted, git-compatible diff files that can be committed to version control or shared via pull requests. Each team member decrypts using their own key derived from a shared passphrase.

---

## License

MIT © [envault contributors](https://github.com/your-org/envault)