# Security Notice

## GitGuardian Alert Resolution

If you received a GitGuardian alert about secrets in this repository, please note:

### What Triggered the Alert
- Example passwords in `.env.example` file
- Default development keys in `config.py` and `docker-compose.yml`

### These Are NOT Real Secrets
- These are **placeholder values** for local development only
- They are clearly marked as "CHANGE_THIS" or "INSECURE_DEV_KEY"
- They are never used in production
- The actual `.env` file (with real secrets) is in `.gitignore`

### For Production Deployment
**NEVER use these placeholder values in production!**

Generate secure secrets:
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

Set these in your production environment variables (Render, Vercel, etc.)

### Best Practices
1. ✅ Always use `.env.example` for templates (committed)
2. ✅ Always add `.env` to `.gitignore` (never commit)
3. ✅ Use environment variables in production
4. ✅ Rotate secrets regularly
5. ✅ Use different secrets for each environment

### If You Accidentally Committed Real Secrets
1. Immediately rotate the compromised secrets
2. Update all production environments
3. Consider using `git filter-branch` or BFG Repo-Cleaner to remove from history
4. Force push to update remote repository

---

**This repository is safe** - no real secrets were exposed. The flagged values are intentionally obvious placeholders for development.
