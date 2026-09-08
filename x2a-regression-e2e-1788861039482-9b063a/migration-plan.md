# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. The repository is already primarily Ansible-based with InSpec used for compliance testing. This represents a hybrid approach rather than a traditional Chef-to-Ansible migration scenario.

## Module Migration Plan

This repository contains demonstration examples and deployment scripts that showcase Chef InSpec integration with Ansible:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache HTTPS web server configuration with SSL certificate generation, virtual host setup, and security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: Self-signed SSL certificates via OpenSSL modules, Apache virtual host configuration, security compliance verification

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL protocol configuration, security compliance remediation

**chef-automate-deployment**:
- Description: Automated deployment script for Chef Automate and Chef Infra Server on VM infrastructure
- Path: setup-automate/deploy-automate.sh
- Technology: Bash
- Key Features: System tuning, Chef Automate CLI deployment, user and organization creation

**chef-server-deployment**:
- Description: Standalone Chef Infra Server deployment without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash
- Key Features: Chef Server installation, user management, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL security
- `tests/ssh_profile.rb`: InSpec security profile for SSH hardening compliance (STIG controls)
- `index.html`: Static web content for testing purposes
- `README.md`: Documentation explaining Chef InSpec and Ansible integration approach

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with RHEL compatibility indicated in InSpec profiles
- **Virtual Machine Technology**: Vagrant (Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

**No traditional Chef dependencies present** - this repository demonstrates integration patterns rather than containing Chef cookbooks requiring migration.

- **Chef InSpec**: Already integrated with Ansible for compliance testing - no migration needed
- **Test Kitchen**: Currently configured for Ansible playbook testing - can be retained or replaced with molecule
- **Apache OpenSSL modules**: Already using Ansible's native openssl_* modules

### Security Considerations

- **SSL/TLS Configuration**: Existing playbooks properly implement SSL certificate generation and security hardening
- **Compliance Testing**: InSpec profiles implement STIG controls for SSH hardening and SSL security
- **Credential Management**: 
  - Chef Server deployment scripts contain hardcoded credentials (usernames, passwords, email addresses)
  - SSL private keys generated in-place without external secret management
  - No vault or encrypted variable usage detected

### Technical Challenges

- **Minimal Migration Required**: Repository is already Ansible-based with InSpec integration
- **Test Framework Decision**: Evaluate whether to continue using Test Kitchen or migrate to Ansible Molecule for testing
- **Credential Security**: Hardcoded credentials in deployment scripts need to be externalized to Ansible Vault or external secret management
- **InSpec Integration**: Determine if Chef InSpec should be retained for compliance or replaced with Ansible-native compliance tools

### Migration Order

1. **Security Hardening** (immediate): Externalize hardcoded credentials from deployment scripts to Ansible Vault
2. **Test Framework Evaluation** (low priority): Assess Test Kitchen vs Molecule for Ansible testing workflow
3. **Compliance Tool Assessment** (medium priority): Evaluate InSpec vs native Ansible compliance approaches

### Assumptions

- This repository serves as demonstration/example code rather than production infrastructure requiring migration
- The hybrid Chef InSpec + Ansible approach is intentional for showcasing compliance automation patterns
- Deployment scripts are for development/lab environments given the hardcoded credentials and simplified setup
- Ubuntu 20.04 target may need updating to more recent LTS versions for production use
- The repository owner intends to maintain the InSpec integration as a key feature rather than eliminate Chef components entirely
- Test Kitchen configuration suggests this is primarily a development/testing repository rather than production infrastructure code