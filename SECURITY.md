# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in the Echo AI Dashboard, please report it privately to the repository maintainers. Do not create public issues for security vulnerabilities.

## Secure Configuration

### Authentication
- Never commit password hashes or access codes to the repository
- Use Streamlit secrets management or environment variables for sensitive data
- Generate strong password hashes using SHA-256 or stronger algorithms
- Rotate passwords regularly

### API Keys
- Store all API keys in environment variables or secure secret management systems
- Never commit API keys to version control
- Use separate keys for development and production environments
- Implement rate limiting to prevent API abuse

### Data Protection
- The dashboard operates in a stateless manner - no user data is persisted
- All data fetched from external APIs is cached temporarily only
- No sensitive financial data is logged or stored permanently

## Security Best Practices

### Input Validation
- All user inputs should be validated and sanitized
- File uploads (if implemented) must be restricted by type and size
- SQL injection prevention through parameterized queries (if database is added)

### Logging
- Avoid logging sensitive information (passwords, API keys, personal data)
- Implement structured logging with appropriate log levels
- Secure log files with appropriate file permissions

### Dependencies
- Regularly update dependencies to patch known vulnerabilities
- Use `pip-audit` or similar tools to scan for vulnerable packages
- Review dependency changes in pull requests

### Network Security
- Use HTTPS for all external API calls
- Implement request timeouts to prevent DoS
- Add rate limiting for API endpoints if exposed

## Known Security Considerations

1. **Default Password**: The default password hash in documentation is for example purposes only and should never be used in production
2. **API Rate Limits**: Yahoo Finance and other providers have rate limits; excessive requests may result in IP blocking
3. **Session Management**: Streamlit's built-in session management is used; ensure proper deployment configuration

## Compliance

This application is designed for personal use and educational purposes. If used in a production environment with real trading data:
- Ensure compliance with financial regulations (SEC, FINRA, etc.)
- Implement audit logging
- Add data retention policies
- Consult legal counsel for regulatory requirements

## Updates

This security policy is subject to updates. Check this document regularly for changes.

Last Updated: December 2025
