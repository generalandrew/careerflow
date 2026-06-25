# Email Inbox Status Sync Runtime

Automated runtime that reads recent emails (Gmail, Outlook, IMAP) and syncs application status updates to `applications.xlsx` and the per-application `metadata.json`. Detects:

- Application receipt confirmations -> `Status = Applied`
- Rejection notices -> `Status = Rejected`
- Interview invitations -> `Status = Interviewing`
- Offer emails -> `Status = Offer`

## Trigger phrases

- `sync email status`
- `check inbox for application updates`
- `run email status sync`

## Setup (one-time)

1. Create `~/.careerflow_email_config.json` with your IMAP credentials:

```json
{
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "email_address": "you@example.com",
    "password_or_app_password": "your-app-specific-password",
    "scan_folders": ["INBOX"],
    "scan_days_back": 14
}
```

2. **Use an app-specific password, never your real password.**
   - Gmail: myaccount.google.com -> Security -> 2-Step Verification -> App passwords
   - Outlook 365: security.microsoft.com -> App passwords
   - Yahoo: account security -> Manage app passwords
3. Add `.careerflow_email_config.json` to your global gitignore. It already lives outside the repo (in your home directory) so it will not be committed by accident.

## Procedure

1. Read `~/.careerflow_email_config.json`.
2. Connect to IMAP, fetch messages from the last N days (default 14).
3. For each message, scan subject + body for trigger patterns (see `scripts/email_status_sync.py` for the regex set).
4. For each match, try to associate with an open application by matching company name in subject or body.
5. Update `metadata.json -> status` and append to `status_history` for each match.
6. Update the matching row in `applications.xlsx -> Status` and `Last Touch`.

## CLI usage

```bash
python3 scripts/email_status_sync.py [--dry-run]
```

`--dry-run` shows what would be updated without writing. Use this for the first run to verify the matching is sane.

## Cadence

Recommended: daily, via the scheduled-tasks MCP or a manual `sync email status` trigger.

## Privacy

- The config file with your password lives in your home directory, never in the repo.
- The script reads emails locally, no data leaves your machine.
- Email content is not stored in the workspace, only the status change is persisted.
