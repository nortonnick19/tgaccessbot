# TG Access Control Deployment


## Services

### API

FastAPI service:

tgaccess-api.service


### Telegram Bot

Telegram control bot:

tgaccess-bot.service


### Firewall Sync

Restore ipset whitelist after reboot:

tgaccess-firewall-sync.service



## Install

Run:

```bash
./deployment/install.sh
