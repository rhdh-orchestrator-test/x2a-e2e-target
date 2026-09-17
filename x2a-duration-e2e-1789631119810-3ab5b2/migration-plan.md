# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec for compliance testing. This represents a **demonstration repository** rather than a production infrastructure codebase requiring migration.

**Migration Scope**: Minimal - Repository already uses Ansible playbooks with Chef InSpec for compliance validation
**Complexity**: Low - No actual Chef cookbooks present
**Timeline**: 1-2 days for cleanup and standardization

## Module Migration Plan

This repository contains example Ansible playbooks and Chef InSpec tests that demonstrate compliance automation patterns:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Apache HTTPS web server deployment with SSL/TLS configuration and POODLE vulnerability remediation
- Path: chef-and-ansible/
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Self-signed certificate generation, Apache virtual host configuration, SSL protocol hardening, compliance verification

**setup-automate**:
- Description: Chef Automate and Chef Infra Server deployment automation scripts
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Automated Chef server installation, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `website_https.yml`: Apache HTTPS server deployment playbook with SSL certificate management
- `poodle_fix.yml`: SSL protocol hardening playbook to disable vulnerable protocols
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `tests/ssh_profile.rb`: InSpec SSH security compliance profile with STIG controls
- `deploy-automate.sh`: Chef Automate deployment script with Infra Server integration
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated for compliance testing - no migration needed
- **Test Kitchen**: Currently configured for Ansible provisioner - maintain existing setup
- **Apache 2.4.41**: Specific version pinned in playbook - verify availability in target environment
- **OpenSSL/PyOpenSSL**: Required for certificate generation - standard Ansible crypto modules used

### Security Considerations

- **SSL/TLS Configuration**: Playbooks implement proper SSL hardening by disabling SSLv3 and enforcing TLS 1.2+
- **Certificate Management**: Uses Ansible's openssl modules for self-signed certificate generation - consider integration with enterprise CA
- **SSH Hardening**: InSpec profiles validate SSH security configurations including root login restrictions
- **Vault/Secrets Management**: 
  - Hardcoded credentials present in Chef server deployment scripts (userpassword='password')
  - No encrypted variables or vault usage detected
  - SSL private keys generated locally without external key management

### Technical Challenges

- **Example Code Nature**: Repository contains demonstration code rather than production-ready infrastructure
- **Hardcoded Values**: Chef server deployment scripts contain hardcoded credentials and configuration
- **Test Environment Focus**: Current setup optimized for testing rather than production deployment
- **InSpec Integration**: Maintaining Chef InSpec for compliance while using Ansible for configuration management

### Migration Order

1. **Standardize Ansible Playbooks** (Priority 1 - low risk, immediate value)
   - Review and enhance existing website_https.yml and poodle_fix.yml playbooks
   - Implement Ansible Vault for credential management
   - Add proper error handling and idempotency checks

2. **Enhance Security Practices** (Priority 2 - moderate complexity)
   - Replace hardcoded credentials in deployment scripts with vault-encrypted variables
   - Implement proper certificate management workflow
   - Add additional InSpec compliance profiles

3. **Production Readiness** (Priority 3 - high complexity)
   - Convert bash deployment scripts to Ansible playbooks
   - Implement proper inventory management
   - Add comprehensive logging and monitoring integration

### Assumptions

- Repository serves as example/demonstration code rather than production infrastructure requiring migration
- Current Ansible playbooks are functional and follow acceptable practices for example purposes
- InSpec integration will be maintained for compliance validation in the target environment
- Test Kitchen workflow will continue to be used for validation and testing
- Ubuntu 20.04 target environment assumption based on kitchen.yml configuration may need verification for production use
- Self-signed certificates are acceptable for demonstration purposes but will require proper CA integration for production
- Chef server deployment scripts represent optional tooling rather than core infrastructure requiring migration