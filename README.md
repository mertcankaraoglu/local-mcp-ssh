# MCP SSH Server 🚀

Manage your Ubuntu/Linux servers from your Windows computer using **natural language**! This MCP (Model Context Protocol) server enables you to control your remote servers through conversation via Claude Desktop or Cursor IDE by establishing SSH connections.

---
TR:
Windows bilgisayarınızdan Ubuntu/Linux sunucularınızı **doğal dil** ile yönetin! Bu MCP (Model Context Protocol) server, Claude Desktop veya Cursor IDE üzerinden SSH bağlantısı yaparak uzak sunucularınızı konuşarak kontrol etmenizi sağlar.

## 🎯 Neden Bu Proje?

Geleneksel SSH yönetimi yerine, AI asistanınıza "Ubuntu sunucuma bağlan ve disk kullanımını göster" diyerek işlerinizi halledebilirsiniz. MCP protokolü sayesinde AI, SSH komutlarını sizin için çalıştırır ve sonuçları gerçek zamanlı olarak size sunar.

## ✨ Özellikler

- 🔐 **Güvenli SSH Bağlantısı** - Şifre tabanlı kimlik doğrulama
- ⚡ **Gerçek Zamanlı Çıktı** - Komut çıktılarını anlık görün
- 🤖 **AI Entegrasyonu** - Claude Desktop ve Cursor IDE desteği
- 🎨 **Doğal Dil Kontrolü** - Komutları konuşarak çalıştırın
- 📦 **Minimal Kurulum** - Sadece 3 tool, sıfır karmaşıklık

## 📋 Gereksinimler

- **Node.js v18 veya üzeri** ([İndir](https://nodejs.org/))
- **Claude Desktop** ([İndir](https://claude.ai/download))
- SSH erişimi olan bir Linux/Ubuntu sunucu

### Node.js Kurulumu

**Windows:**
1. [nodejs.org](https://nodejs.org/) adresinden LTS versiyonunu indirin
2. İndirilen `.msi` dosyasını çalıştırın
3. Kurulum tamamlandıktan sonra terminal açın ve `node --version` yazın

**macOS:**
```bash
# Homebrew ile
brew install node

# Veya resmi site'den indirin
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 🚀 Kurulum

### 1. Projeyi İndirin

```bash
git clone https://github.com/YOUR_USERNAME/local-mcp-ssh.git
cd local-mcp-ssh
```

### 2. Bağımlılıkları Yükleyin

```bash
npm install
```

### 3. MCP'yi Bağlayın

Kullandığınız uygulamaya göre aşağıdaki adımları izleyin:

#### 🖥️ Claude Desktop için

**Windows:**

`%APPDATA%\Claude\claude_desktop_config.json` dosyasını açın ve ekleyin:

```json
{
  "mcpServers": {
    "ssh": {
      "command": "node",
      "args": ["C:\\Users\\KULLANICI_ADINIZ\\local-mcp-ssh\\index.js"]
    }
  }
}
```

**macOS/Linux:**

`~/Library/Application Support/Claude/claude_desktop_config.json` dosyasını açın:

```json
{
  "mcpServers": {
    "ssh": {
      "command": "node",
      "args": ["/tam/yol/local-mcp-ssh/index.js"]
    }
  }
}
```

#### 🎯 Cursor IDE için

**Windows:**

`%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json` dosyasını açın:

```json
{
  "mcpServers": {
    "ssh": {
      "command": "node",
      "args": ["C:\\Users\\KULLANICI_ADINIZ\\local-mcp-ssh\\index.js"]
    }
  }
}
```

**macOS/Linux:**

`~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "ssh": {
      "command": "node",
      "args": ["/tam/yol/local-mcp-ssh/index.js"]
    }
  }
}
```

### 4. Uygulamayı Yeniden Başlatın

Claude Desktop veya Cursor'ı kapatıp tekrar açın. MCP server otomatik olarak başlayacaktır.

### 5. Kurulumu Test Edin

Claude Desktop'ta şu komutu deneyin:
```
"SSH bağlantısı test et - 192.168.1.100 IP'li sunucuya bağlan"
```

Eğer MCP server çalışıyorsa, Claude size SSH bağlantı parametrelerini soracaktır.

## 💡 Kullanım

### Mevcut Araçlar

| Araç | Açıklama |
|------|----------|
| `ssh_connect` | SSH sunucusuna bağlantı kur |
| `ssh_exec` | Uzak sunucuda komut çalıştır |
| `ssh_disconnect` | SSH bağlantısını kapat |

### Örnek Konuşmalar

**Bağlantı Kurma:**
```
Siz: "192.168.1.100 IP'li Ubuntu sunucuma bağlan. Kullanıcı adı: ubuntu, şifre: mypassword"
Claude: [ssh_connect aracını kullanarak bağlanır]
```

**Komut Çalıştırma:**
```
Siz: "Disk kullanımını göster"
Claude: [ssh_exec ile 'df -h' komutunu çalıştırır]

Siz: "Son 10 sistem logunu göster"
Claude: [ssh_exec ile 'tail -n 10 /var/log/syslog' çalıştırır]

Siz: "Docker container'larını listele"
Claude: [ssh_exec ile 'docker ps' çalıştırır]
```

**Bağlantıyı Kapatma:**
```
Siz: "SSH bağlantısını kapat"
Claude: [ssh_disconnect aracını kullanır]
```

## 🔧 Teknik Detaylar

### Kullanılan Teknolojiler

- **[@modelcontextprotocol/sdk](https://github.com/modelcontextprotocol/sdk)** - MCP protokol implementasyonu
- **[ssh2](https://github.com/mscdex/ssh2)** - SSH2 client kütüphanesi

### Mimari

```
┌─────────────────┐
│ Claude/Cursor   │
│   (AI Client)   │
└────────┬────────┘
         │ MCP Protocol
         │ (stdio)
┌────────▼────────┐
│  MCP SSH Server │
│   (Bu Proje)    │
└────────┬────────┘
         │ SSH2
         │
┌────────▼────────┐
│ Ubuntu Server   │
└─────────────────┘
```

## 🛡️ Güvenlik Notları

- ⚠️ Şifreler düz metin olarak config dosyasında saklanmaz, sadece runtime'da kullanılır
- 🔒 SSH bağlantıları standart SSH2 protokolü ile şifrelenir
- 💡 Üretim ortamları için SSH key tabanlı kimlik doğrulama önerilir (gelecek sürümlerde eklenecek)

## 🗺️ Yol Haritası

- [ ] SSH key desteği
- [ ] Çoklu sunucu yönetimi
- [ ] SFTP dosya transferi
- [ ] Port forwarding
- [ ] Session kaydetme/yükleme

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull request göndermekten çekinmeyin.

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit edin (`git commit -m 'feat: Add amazing feature'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

## 📝 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- [Anthropic](https://anthropic.com) - Claude ve MCP protokolü için
- [Model Context Protocol](https://modelcontextprotocol.io) - Harika dokümantasyon için

---

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**

---

# ENG - English Documentation

## 🎯 Why This Project?

Instead of traditional SSH management, you can handle your tasks by simply telling your AI assistant "Connect to my Ubuntu server and show disk usage". Thanks to the MCP protocol, AI executes SSH commands for you and presents results in real-time.

## ✨ Features

- 🔐 **Secure SSH Connection** - Password-based authentication
- ⚡ **Real-Time Output** - See command outputs instantly
- 🤖 **AI Integration** - Claude Desktop and Cursor IDE support
- 🎨 **Natural Language Control** - Execute commands by speaking
- 📦 **Minimal Setup** - Only 3 tools, zero complexity

## 📋 Requirements

- Node.js v18 or higher
- Claude Desktop or Cursor IDE
- A Linux/Ubuntu server with SSH access

## 🚀 Installation

### 1. Clone the Project

```bash
git clone https://github.com/YOUR_USERNAME/local-mcp-ssh.git
cd local-mcp-ssh
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Connect MCP

Follow the steps below according to your application:

#### 🖥️ For Claude Desktop

**Windows:**

Open `%APPDATA%\Claude\claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "ssh": {
      "command": "node",
      "args": ["C:\\Users\\YOUR_USERNAME\\local-mcp-ssh\\index.js"]
    }
  }
}
```

**macOS/Linux:**

Open `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ssh": {
      "command": "node",
      "args": ["/full/path/local-mcp-ssh/index.js"]
    }
  }
}
```

#### 🎯 For Cursor IDE

**Windows:**

Open `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "ssh": {
      "command": "node",
      "args": ["C:\\Users\\YOUR_USERNAME\\local-mcp-ssh\\index.js"]
    }
  }
}
```

**macOS/Linux:**

`~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "ssh": {
      "command": "node",
      "args": ["/full/path/local-mcp-ssh/index.js"]
    }
  }
}
```

### 4. Restart the Application

Close and reopen Claude Desktop or Cursor. The MCP server will start automatically.

## 💡 Usage

### Available Tools

| Tool | Description |
|------|-------------|
| `ssh_connect` | Establish SSH connection to server |
| `ssh_exec` | Execute command on remote server |
| `ssh_disconnect` | Close SSH connection |

### Example Conversations

**Connecting:**
```
You: "Connect to my Ubuntu server at 192.168.1.100. Username: ubuntu, password: mypassword"
Claude: [Connects using ssh_connect tool]
```

**Running Commands:**
```
You: "Show disk usage"
Claude: [Executes 'df -h' command via ssh_exec]

You: "Show last 10 system logs"
Claude: [Executes 'tail -n 10 /var/log/syslog' via ssh_exec]

You: "List Docker containers"
Claude: [Executes 'docker ps' via ssh_exec]
```

**Disconnecting:**
```
You: "Close SSH connection"
Claude: [Uses ssh_disconnect tool]
```

## 🔧 Technical Details

### Technologies Used

- **[@modelcontextprotocol/sdk](https://github.com/modelcontextprotocol/sdk)** - MCP protocol implementation
- **[ssh2](https://github.com/mscdex/ssh2)** - SSH2 client library

### Architecture

```
┌─────────────────┐
│ Claude/Cursor   │
│   (AI Client)   │
└────────┬────────┘
         │ MCP Protocol
         │ (stdio)
┌────────▼────────┐
│  MCP SSH Server │
│  (This Project) │
└────────┬────────┘
         │ SSH2
         │
┌────────▼────────┐
│ Ubuntu Server   │
└─────────────────┘
```

## 🛡️ Security Notes

- ⚠️ Passwords are not stored in config files as plain text, only used at runtime
- 🔒 SSH connections are encrypted with standard SSH2 protocol
- 💡 SSH key-based authentication is recommended for production environments (will be added in future versions)

## 🗺️ Roadmap

- [ ] SSH key support
- [ ] Multi-server management
- [ ] SFTP file transfer
- [ ] Port forwarding
- [ ] Session save/load

## 🤝 Contributing

We welcome your contributions! Feel free to send pull requests.

1. Fork it
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) - For Claude and MCP protocol
- [Model Context Protocol](https://modelcontextprotocol.io) - For excellent documentation

---

**⭐ Don't forget to star the project if you like it!**
