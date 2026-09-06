# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and demonstration materials rather than production infrastructure-as-code that requires migration. The repository demonstrates Chef InSpec integration with Ansible playbooks and includes Chef Automate/Chef Server deployment scripts. The migration scope is minimal as the primary content is already Ansible-based with supporting Chef InSpec tests and deployment utilities.

## Module Migration Plan

This repository contains demonstration and utility content rather than traditional modules requiring migration:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

**Ansible Playbooks (Already Migrated):**
- **website_https**:
    - Description: Apache HTTPS website deployment with SSL certificate generation, virtual host configuration, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Self-signed SSL certificates via OpenSSL, Apache virtual host configuration, package management, service handlers

- **poodle_fix**:
    - Description: SSL/TLS security hardening playbook to disable vulnerable SSL protocols and enforce TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration remediation, service restart handlers, POODLE vulnerability mitigation

**Chef InSpec Test Profiles:**
- **ssh_profile**:
    - Description: SSH security compliance test ensuring root login is disabled per STIG requirements
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: STIG compliance validation (RHEL-08-000227), SSH configuration testing, security control verification

- **website_https_verify**:
    - Description: HTTPS website functionality and SSL/TLS security validation tests
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port 443 listening verification, HTTP response validation, SSL protocol security testing

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Static HTML test content for website deployment validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment automation script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `README.md`: Repository documentation explaining Chef InSpec and Ansible integration examples

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml test configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Already integrated with Ansible via Test Kitchen - no migration needed
- **Test Kitchen**: Currently used for testing Ansible playbooks with InSpec verification - consider migrating to molecule for pure Ansible testing
- **Apache 2.4.41**: Specific version pinned in playbook - update to latest stable version during migration
- **OpenSSL Python bindings**: Required for SSL certificate generation - ensure python3-openssl package availability

### Security Considerations
- **SSL/TLS Configuration**: Existing playbooks implement proper SSL hardening with TLS 1.2 enforcement and SSL 3.0 disabling
- **Self-signed Certificates**: Current implementation uses self-signed certificates - consider integration with Let's Encrypt or enterprise CA for production
- **SSH Hardening**: InSpec tests validate SSH root login disabling per STIG requirements
- **Vault/secrets management**: 
  - Hardcoded credentials detected in deployment scripts (setup-automate/*.sh) - 7 credential instances including usernames, passwords, and email addresses
  - No encrypted secrets or vault usage detected in Ansible playbooks
  - SSL private keys generated dynamically without external secret management

### Technical Challenges
- **Test Framework Migration**: Consider migrating from Test Kitchen + InSpec to Ansible Molecule for unified testing approach
- **Deployment Script Integration**: Shell scripts for Chef server deployment may need conversion to Ansible playbooks for consistency
- **InSpec Dependency**: Maintaining Chef InSpec for compliance testing while using Ansible for configuration management creates tool diversity

### Migration Order
1. **Ansible Playbooks** (already complete - no migration needed)
2. **Test Framework** (optional - migrate Test Kitchen to Molecule)
3. **Deployment Scripts** (convert shell scripts to Ansible playbooks)
4. **Documentation Update** (update examples to reflect pure Ansible approach)

### Assumptions
- This repository serves as demonstration/example content rather than production infrastructure requiring migration
- The primary value is in the Chef InSpec integration pattern with Ansible, which may be preserved
- Test Kitchen configuration assumes Vagrant availability for local testing
- Deployment scripts target Linux environments with systemctl and standard package managers
- SSL certificate requirements are for testing/development rather than production use
- The repository maintainers may prefer to keep Chef InSpec integration as a demonstration of hybrid toolchain approaches
- Network connectivity to Chef package repositories is assumed for deployment script execution
- Root or sudo access is assumed for all deployment and configuration tasks