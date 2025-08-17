---
type: "manual"
---

# Security & Compliance Rules for Financial Applications

**CRITICAL: This project handles sensitive financial data and MUST comply with financial data protection standards.**

## Mandatory Security Requirements

### Financial Data Protection Standards

**BEFORE any financial data processing implementation:**

1. **PCI-DSS Compliance Assessment**
   - Document data classification (cardholder data vs. sensitive authentication data)
   - Implement secure data storage requirements
   - Define access control and authentication mechanisms
   - Establish audit logging and monitoring

2. **Privacy Regulation Compliance**
   - **GDPR**: Right to erasure, data portability, consent management
   - **CCPA**: Consumer privacy rights and data disclosure requirements
   - **Regional**: Additional local privacy laws as applicable

3. **Encryption Standards**
   - **At Rest**: AES-256 encryption for all financial data storage
   - **In Transit**: TLS 1.3 minimum for all API communications
   - **Key Management**: Secure key rotation and storage practices

### Security Architecture Requirements

**MANDATORY security layers for all financial applications:**

```
User Interface (Flutter)
    ↓ [HTTPS/TLS 1.3]
API Gateway + Rate Limiting
    ↓ [JWT + API Keys]
Authentication & Authorization Layer
    ↓ [Encrypted Channels]
Business Logic (Python/FastAPI)
    ↓ [Encrypted Connections]
Database Layer (Encrypted at Rest)
```

### Data Handling Rules

**Financial Data Classification:**
- **Level 1 (Public)**: General budget categories, non-sensitive preferences
- **Level 2 (Internal)**: Aggregated spending patterns, anonymized insights
- **Level 3 (Confidential)**: Account balances, transaction details, personal identifiers
- **Level 4 (Restricted)**: Authentication credentials, encryption keys, audit logs

**Data Processing Requirements:**
- Implement data minimization principles
- Use tokenization for sensitive data references
- Establish data retention and deletion policies
- Implement secure data export/import mechanisms

### AI System Security

**LLM and AI Agent Security:**
- **Input Sanitization**: Validate all user inputs before AI processing
- **Output Filtering**: Screen AI responses for sensitive data leakage
- **Prompt Injection Protection**: Implement guardrails against malicious prompts
- **Model Access Control**: Secure API keys and model access permissions

### Development Security Practices

**Secure Development Lifecycle:**

1. **Threat Modeling** (Required before Phase 1)
   - Identify attack vectors and threat actors
   - Document security controls and mitigations
   - Regular security architecture reviews

2. **Security Testing** (Required each phase)
   - Static Application Security Testing (SAST)
   - Dynamic Application Security Testing (DAST)
   - Dependency vulnerability scanning
   - Penetration testing for production releases

3. **Secure Configuration Management**
   - Environment-specific security configurations
   - Secrets management (never hardcode credentials)
   - Regular security updates and patches

### Compliance Documentation Requirements

**MANDATORY documentation before production:**

1. **Security Policy Document**
   - Data classification and handling procedures
   - Incident response and breach notification plans
   - Access control and user management policies

2. **Privacy Policy and Terms of Service**
   - Clear data collection and usage statements
   - User consent mechanisms and opt-out procedures
   - Third-party data sharing disclosures

3. **Audit and Monitoring Plan**
   - Security event logging requirements
   - Regular compliance assessments schedule
   - Vulnerability management procedures

### Integration Security

**Multi-System Security (CrewAI + Archon + Master Agent):**
- Implement secure inter-service communication
- Define trust boundaries and authentication between systems
- Establish consistent security logging across all components
- Coordinate security updates and patches across systems

### Emergency Procedures

**Security Incident Response:**
1. Immediate containment and system isolation
2. User notification within regulatory timeframes
3. Forensic analysis and root cause investigation
4. Remediation and system hardening
5. Regulatory reporting and compliance updates

**Data Breach Response:**
- Automated detection and alerting systems
- Predefined communication templates
- Legal and regulatory notification procedures
- User impact assessment and mitigation plans

## Validation Checklist

**Before any production deployment:**
- [ ] Security architecture review completed
- [ ] Threat model documented and approved
- [ ] Encryption implementation verified
- [ ] Compliance requirements mapped and implemented
- [ ] Security testing completed with no critical findings
- [ ] Incident response procedures tested
- [ ] Privacy policies and user consent mechanisms active
- [ ] Audit logging and monitoring operational

**VIOLATION CONSEQUENCES:**
Failure to implement these security requirements before handling financial data constitutes a critical compliance violation and must halt development until resolved.
