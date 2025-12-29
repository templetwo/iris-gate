# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please email security concerns to: **security@thetempleoftwo.com**

Please include:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if known)

### What to expect

1. **Acknowledgment:** You should receive a response within 48 hours acknowledging receipt of your report.
2. **Investigation:** We will investigate the issue and determine its severity and impact.
3. **Updates:** We will keep you informed about the progress of the fix.
4. **Resolution:** Once the vulnerability is confirmed and fixed:
   - We will release a security patch as soon as possible
   - We will credit you in the release notes (unless you prefer to remain anonymous)
   - We will publish a security advisory on GitHub

## Security Best Practices

When using IRIS Gate:

### API Key Management
- **Never commit API keys** to version control
- Use `.env` files for API keys (already in `.gitignore`)
- Rotate API keys regularly (at least quarterly)
- Use separate API keys for development and production

### Model Output Review
- **Review model outputs** for sensitive data before sharing publicly
- Be cautious when experimenting with proprietary research questions
- Sanitize any logs or scrolls before publishing

### Network Security
- Use HTTPS for all API calls (enabled by default)
- Consider using a VPN when working with sensitive research
- Monitor API usage for anomalies

### Data Privacy
- IRIS Gate does not store your prompts or outputs on our servers
- All data stays local or with your chosen AI providers
- Review each provider's data retention policies:
  - [Anthropic](https://www.anthropic.com/legal/privacy)
  - [OpenAI](https://openai.com/policies/privacy-policy)
  - [Google](https://policies.google.com/privacy)
  - [xAI](https://x.ai/legal/privacy-policy)
  - [DeepSeek](https://www.deepseek.com/privacy)

## Known Security Considerations

### API Rate Limiting
- Malicious actors could trigger excessive API calls
- Mitigation: Implement your own rate limiting if exposing IRIS Gate publicly

### Model Prompt Injection
- Adversarial prompts could potentially manipulate model outputs
- Mitigation: Review convergence results critically, especially for TYPE 2-3 classifications

### Supply Chain
- IRIS Gate depends on third-party packages (see `requirements.txt`)
- We use Dependabot to monitor for vulnerable dependencies
- Keep dependencies updated: `pip install --upgrade -r requirements.txt`

## Security Updates

Security patches will be announced through:
- GitHub Security Advisories
- Release notes with `[SECURITY]` prefix
- Discussions in the Security category

## Responsible Disclosure

We appreciate the security research community's efforts. If you discover a vulnerability:
- Give us reasonable time to fix it before public disclosure
- We will work with you on a coordinated disclosure timeline
- We will credit you publicly (if desired) once the fix is released

Thank you for helping keep IRIS Gate secure!
