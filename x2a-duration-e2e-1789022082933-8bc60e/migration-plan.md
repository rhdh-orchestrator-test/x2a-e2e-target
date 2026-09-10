# MIGRATION FROM MIXED ANSIBLE/CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples of using Chef InSpec alongside Ansible for compliance automation, plus Chef server deployment scripts. The repository is primarily educational and does not contain traditional Chef cookbooks requiring migration. Instead, it demonstrates a hybrid approach where Ansible handles configuration management while Chef InSpec provides compliance testing.

## Module Migration Plan

This repository contains mixed technologies that require different migration approaches:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates, virtual host setup, and SSL protocol hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already target technology)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, SSL/TLS security hardening

**poodle-fix-demo**:
- Description: Ansible playbook for SSL protocol hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already target technology)
- Key Features: Apache SSL configuration modification, protocol restriction, service restart handling

**chef-automate-deployment**:
- Description: Bash script for automated deployment of Chef Automate and Chef Infra Server with user and organization setup
- Path: setup-automate/deploy-automate.sh
- Technology: Bash scripting
- Key Features: Hostname configuration, system tuning, Chef Automate CLI deployment, user/org creation

**chef-server-deployment**:
- Description: Bash script for standalone Chef Infra Server deployment without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash scripting
- Key Features: Similar to automate deployment but infra-server only, user/org management

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration using Vagrant driver with Ansible provisioner and InSpec verifier for integration testing
- `tests/website_https_verify.rb`: Chef InSpec compliance tests verifying HTTPS functionality, SSL protocol configuration, and security posture
- `tests/ssh_profile.rb`: Chef InSpec security control testing SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test content for web server validation
- `README.md`: Documentation explaining the Chef InSpec and Ansible integration approach

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible compliance modules or maintain hybrid approach using ansible.posix.inspec module
- **Test Kitchen**: Replace with Molecule for Ansible testing framework
- **Chef Automate/Server**: Evaluate need for centralized configuration management - consider AWX/Ansible Tower for enterprise orchestration

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks demonstrate proper SSL hardening practices that should be maintained
  - Self-signed certificate generation for development/testing
  - SSL protocol restriction (TLS 1.2 minimum)
  - Apache SSL module configuration
- **SSH Hardening**: InSpec tests verify SSH root login restrictions - ensure Ansible playbooks implement equivalent hardening
- **Credential Management**: Deployment scripts contain hardcoded credentials that need to be externalized to Ansible Vault
  - Username/password combinations in deployment scripts
  - Certificate and key file management
  - Organization and user creation credentials

### Technical Challenges

- **Testing Framework Migration**: Converting from Test Kitchen + InSpec to Molecule + Ansible testing requires restructuring test approach
- **Compliance Testing**: Deciding whether to maintain Chef InSpec for compliance or migrate to native Ansible compliance modules
- **Deployment Script Conversion**: Bash deployment scripts need conversion to Ansible playbooks for consistency and idempotency
- **Integration Testing**: Maintaining the same level of integration testing coverage during framework transition

### Migration Order

1. **Deployment Scripts** (low risk, high value) - Convert bash scripts to Ansible playbooks for Chef server deployment
2. **Testing Framework** (moderate complexity) - Migrate from Test Kitchen to Molecule for consistent testing approach  
3. **Compliance Integration** (high complexity) - Evaluate and potentially migrate from Chef InSpec to Ansible-native compliance testing

### Assumptions

- The repository serves as demonstration/educational content rather than production infrastructure code
- Current Ansible playbooks are already following best practices and don't require significant refactoring
- Chef InSpec compliance tests may be retained in a hybrid approach if Ansible-native alternatives don't provide equivalent functionality
- Test Kitchen integration testing approach needs to be preserved in the migration to Molecule
- Deployment scripts are used for development/lab environments rather than production (given hardcoded credentials)
- The target audience understands both Chef InSpec and Ansible ecosystems for the educational content
- SSL certificate management approach (self-signed for demo) is appropriate for the intended use case
- Ubuntu 20.04 target platform will remain consistent post-migration