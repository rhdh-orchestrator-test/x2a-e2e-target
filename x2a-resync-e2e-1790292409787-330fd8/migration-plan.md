# MIGRATION FROM CHEF INFRASTRUCTURE TO ANSIBLE

This repository is a Chef examples collection that contains Ansible playbooks, Chef InSpec compliance tests, and Chef infrastructure deployment scripts. Rather than containing traditional Chef cookbooks that require migration, this repository demonstrates integration patterns between Chef InSpec and Ansible. The migration scope is minimal as the core automation is already implemented in Ansible.

## Module Migration Plan

This repository contains demonstration and infrastructure setup content rather than production Chef cookbooks requiring migration:

### MODULE INVENTORY

**No Chef cookbooks or recipes found for migration.** This repository contains:

- **website-https-demo**: 
  - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS hardening, and virtual host setup
  - Path: chef-and-ansible/website_https.yml
  - Technology: Ansible (already migrated)
  - Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, security hardening

- **poodle-ssl-fix**: 
  - Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 (POODLE vulnerability mitigation)
  - Path: chef-and-ansible/poodle_fix.yml
  - Technology: Ansible (already migrated)
  - Key Features: Apache SSL configuration updates, protocol restriction, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Ansible provisioner with InSpec verifier for compliance testing
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol verification, and port availability
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `chef-and-ansible/index.html`: Static HTML test content for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for infrastructure setup
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies requiring migration.** The Ansible playbooks use standard modules:
- **apache2 (2.4.41-4ubuntu3.10)**: Already using Ansible apt module for package management
- **openssl/python3-openssl**: Certificate generation handled by Ansible openssl_* modules
- **curl**: Standard system utility installation via Ansible apt module

### Security Considerations

**Existing security implementations in Ansible playbooks:**
- SSL/TLS certificate management: Self-signed certificate generation with proper file permissions (0640 for certs directory)
- Protocol hardening: POODLE vulnerability mitigation by disabling SSLv3 and enforcing TLS 1.2
- SSH security: InSpec compliance testing for SSH root login restrictions following STIG guidelines
- File permissions: Proper ownership and permissions for web content (0644) and configuration files (0640)

**Vault/secrets management:** 
- Hardcoded credentials present in deployment scripts (userpassword='password' in setup scripts)
- SSL private keys generated dynamically but stored in plaintext on filesystem
- No encrypted data bags or vault usage detected

### Technical Challenges

**Minimal migration challenges as content is already in Ansible:**
- InSpec integration: The repository demonstrates Chef InSpec for compliance testing alongside Ansible - this pattern should be preserved
- Test Kitchen workflow: Current testing uses kitchen-ansible provisioner with InSpec verifier - consider migrating to molecule for Ansible-native testing
- Deployment script modernization: Bash deployment scripts could be converted to Ansible playbooks for consistency

### Migration Order

**No traditional migration required, but modernization opportunities:**
1. **Infrastructure deployment** (convert bash scripts to Ansible playbooks for Chef server deployment)
2. **Testing framework** (evaluate migration from Test Kitchen to Molecule for Ansible-native testing)
3. **Compliance integration** (maintain InSpec integration patterns for continuous compliance)

### Assumptions

- This repository serves as a demonstration/example collection rather than production infrastructure code
- The existing Ansible playbooks are functional and represent the target state rather than source material for migration
- Chef InSpec compliance testing integration should be preserved as it demonstrates value-add compliance automation
- The deployment scripts are for setting up Chef infrastructure to support other Chef-based environments, not for migration
- Ubuntu 20.04 target platform is appropriate for the demonstration environment
- Self-signed certificates are acceptable for demonstration purposes but would need proper CA-signed certificates in production
- The hardcoded credentials in deployment scripts are acceptable for demo/lab environments but require proper secrets management for production use