# Public repository setup

Repository: `homegundredaroad/Vaping26`

## GitHub Actions

No external API keys are required for public validation.

Hostinger deployment is optional and manual in the bootstrap release. Configure it only after the target site/directory is known.

### Repository Secrets for Hostinger

- `HOSTINGER_HOST` — SSH/SFTP hostname or IP from hPanel.
- `HOSTINGER_USERNAME` — SSH/SFTP username.
- `HOSTINGER_SSH_PRIVATE_KEY` — private half of a dedicated deploy key. Never commit it.

### Repository Variables for Hostinger

- `HOSTINGER_PORT` — normally the SSH port shown in hPanel (Hostinger commonly uses 65002; use the value shown for the account).
- `HOSTINGER_TARGET_DIR` — absolute deployment directory, for example `/home/USER/domains/DOMAIN/public_html`.

The matching public SSH key must be added to Hostinger before deployment.

## Publication source

Approved research outputs should arrive from the private `Vaping26-Research` repository through the publication firewall. The public repository must not pull raw research data from the private repository.
