# MIGRATION FROM MIXED INFRASTRUCTURE TO ANSIBLE

This repository contains example Ansible playbooks, Chef InSpec compliance tests, and Chef server deployment scripts. **No actual migration is required** as the primary infrastructure automation is already implemented in Ansible. This is a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance validation.

## Module Migration Plan

This repository contains demonstration content rather than production infrastructure code requiring migration:

### MODULE INVENTORY

**No modules require migration** - the repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already target technology)
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, SSL configuration, virtual host management

- **poodle_fix**:
    - Description: Ansible playbook for SSL/TLS security hardening to disable vulnerable SSL protocols and enforce TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already target technology)
    - Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL/TLS security validation
- `tests/ssh_profile.rb`: Chef InSpec compliance profile for SSH security hardening (STIG compliance)
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate and Chef Infra Server deployment
- `setup-automate/deploy-chef-server.sh`: Bash script for standalone Chef Infra Server deployment
- `index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No external dependencies requiring migration** - current setup uses:
- **Apache 2.4.41**: Already managed via Ansible apt module
- **OpenSSL/PyOpenSSL**: Certificate management handled by Ansible openssl modules
- **Chef InSpec**: Compliance testing framework (complementary to Ansible, not requiring migration)

### Security Considerations

**Existing security practices to maintain:**
- SSL/TLS certificate management: Self-signed certificates generated via Ansible openssl modules
- Protocol hardening: TLS 1.2 enforcement, SSL 3.0 disabled for POODLE vulnerability mitigation
- SSH security: InSpec tests validate SSH root login restrictions and security configurations
- File permissions: Proper certificate file permissions (0640) and web content permissions (0644/0755)

**Credential management:**
- Hardcoded credentials in Chef server deployment scripts (userpassword='password')
- Self-signed certificates generated dynamically (no credential storage issues)
- No encrypted data bags or vault usage detected

### Technical Challenges

**No significant migration challenges** - this is primarily a demonstration repository:
- Challenge 1: Chef server deployment scripts are standalone and don't require migration to Ansible
- Challenge 2: InSpec compliance tests provide value as-is for continuous compliance validation
- Challenge 3: Existing Ansible playbooks may need production hardening (remove hardcoded values, add error handling)

### Migration Order

**No migration required** - recommended actions for production use:
1. Review and harden existing Ansible playbooks (remove test-specific configurations)
2. Integrate InSpec compliance tests into CI/CD pipeline
3. Consider migrating Chef server deployment scripts to Ansible if automated deployment is needed

### Assumptions

- This repository serves as a demonstration/example rather than production infrastructure code
- The Chef InSpec tests are intended to complement Ansible automation for compliance validation
- Chef server deployment scripts are for lab/development environments (contain hardcoded credentials)
- The Ansible playbooks are functional examples that may need production hardening
- No actual Chef cookbooks exist in this repository requiring migration to Ansible
- The mixed technology approach (Ansible + InSpec) is intentional for demonstrating compliance automation patterns