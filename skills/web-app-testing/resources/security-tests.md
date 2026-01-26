# Security Testing Checklist

## Authentication Security
- [ ] Passwords are hashed (bcrypt, Argon2)
- [ ] Password requirements enforce strong passwords
- [ ] Account lockout after failed login attempts
- [ ] Multi-factor authentication available
- [ ] Session tokens are securely generated
- [ ] Session timeout after inactivity
- [ ] Secure logout clears all session data
- [ ] "Remember me" uses secure mechanisms

## Authorization
- [ ] Role-based access control (RBAC) enforced
- [ ] Users can only access their own data
- [ ] Admin functions require admin privileges
- [ ] API endpoints verify user permissions
- [ ] Direct object reference attacks prevented
- [ ] Privilege escalation attempts blocked

## Input Validation
- [ ] All user input is validated server-side
- [ ] SQL injection attempts are blocked
- [ ] NoSQL injection attempts are blocked
- [ ] Command injection attempts are blocked
- [ ] File upload validation prevents malicious files
- [ ] File size limits prevent DoS
- [ ] Special characters are properly escaped

## XSS (Cross-Site Scripting) Protection
- [ ] User input is HTML-escaped in output
- [ ] Content Security Policy (CSP) headers configured
- [ ] No innerHTML with user-generated content
- [ ] Script tags in user content are sanitized
- [ ] Event handlers in user content are blocked
- [ ] URL parameters are properly escaped

## CSRF (Cross-Site Request Forgery) Protection
- [ ] CSRF tokens on all state-changing forms
- [ ] SameSite cookie attribute set appropriately
- [ ] Origin header validation on sensitive endpoints
- [ ] Custom request headers for AJAX calls
- [ ] Double-submit cookie pattern implemented

## Session Security
- [ ] Session IDs are cryptographically random
- [ ] Session fixation attacks prevented
- [ ] Secure flag set on cookies (HTTPS only)
- [ ] HttpOnly flag prevents JavaScript access
- [ ] SameSite attribute prevents CSRF
- [ ] Session invalidation on password change
- [ ] Concurrent session limits enforced

## Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] TLS/SSL for all data in transit
- [ ] Database credentials not in source code
- [ ] API keys stored securely
- [ ] PII data access logged
- [ ] Data retention policies enforced
- [ ] Secure deletion of sensitive data

## API Security
- [ ] Rate limiting on all API endpoints
- [ ] API authentication required
- [ ] API versioning implemented
- [ ] Input validation on all API parameters
- [ ] Output encoding prevents injection
- [ ] Error messages don't leak sensitive info
- [ ] CORS properly configured

## Headers & Configuration
- [ ] X-Frame-Options prevents clickjacking
- [ ] X-Content-Type-Options prevents MIME sniffing
- [ ] Strict-Transport-Security enforces HTTPS
- [ ] X-XSS-Protection header set
- [ ] Content-Security-Policy configured
- [ ] Referrer-Policy limits information leakage
- [ ] Permissions-Policy restricts features

## Error Handling
- [ ] Error messages don't reveal system details
- [ ] Stack traces not shown in production
- [ ] Database errors don't leak schema info
- [ ] 404 pages don't confirm file existence
- [ ] Error logging doesn't include sensitive data

## Third-Party Security
- [ ] Third-party dependencies kept up-to-date
- [ ] npm audit / vulnerability scanning automated
- [ ] Subresource Integrity (SRI) for CDN resources
- [ ] Third-party scripts loaded from trusted sources
- [ ] Third-party API keys properly secured

## File Upload Security
- [ ] File type validation on server-side
- [ ] File content validation (magic numbers)
- [ ] Files stored outside web root
- [ ] Uploaded files virus scanned
- [ ] File execution permissions restricted
- [ ] Unique filenames prevent overwriting

## Sensitive Operations
- [ ] Password changes require current password
- [ ] Email changes require confirmation
- [ ] Account deletion requires confirmation
- [ ] Payment operations use tokenization
- [ ] Two-factor authentication for sensitive actions

## Client-Side Security
- [ ] No sensitive data in JavaScript
- [ ] No API keys in client-side code
- [ ] LocalStorage doesn't store sensitive data
- [ ] Console.log doesn't leak sensitive info
- [ ] Source maps not deployed to production

## Infrastructure Security
- [ ] HTTPS enforced (no mixed content)
- [ ] TLS 1.2 or higher required
- [ ] Strong cipher suites configured
- [ ] Certificate is valid and not expired
- [ ] HSTS preload list enrollment considered
- [ ] Security headers configured on server

## Logging & Monitoring
- [ ] Failed login attempts logged
- [ ] Suspicious activities logged
- [ ] Security events trigger alerts
- [ ] Logs don't contain passwords/tokens
- [ ] Log retention policy implemented
- [ ] Security incident response plan exists

## Compliance & Privacy
- [ ] GDPR compliance (if applicable)
- [ ] CCPA compliance (if applicable)
- [ ] Cookie consent banner present
- [ ] Privacy policy accessible
- [ ] Terms of service accessible
- [ ] Data breach notification procedures

## Testing-Specific Security
- [ ] Test credentials different from production
- [ ] Test data doesn't contain real PII
- [ ] Test environment isolated from production
- [ ] Security headers present in all environments
- [ ] Vulnerability scanning performed regularly
