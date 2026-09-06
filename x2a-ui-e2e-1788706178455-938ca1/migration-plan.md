# MIGRATION FROM ANSIBLE TO ANSIBLE

This repository is already using Ansible as the primary configuration management technology. The repository contains Ansible playbooks with Chef InSpec compliance testing integration. No migration from another configuration management tool is required, but modernization and optimization opportunities exist.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec compliance tests that demonstrate integration patterns:

### MODULE INVENTORY

**ansible-apache-https**:
- Description: Apache web server deployment with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: SSL certificate generation via OpenSSL modules, Apache virtual host configuration, Hello World website deployment, service management with handlers

**ansible-ssl-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: POODLE vulnerability mitigation, SSL protocol configuration via regex replacement, Apache service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Vagrant driver and InSpec verifier
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, port listening verification, and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG control)
- `chef-and-ansible/index.html`: Static HTML test file for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for testing infrastructure
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

Since this is already an Ansible repository, dependencies are minimal:
- **apache2 (2.4.41-4ubuntu3.10)**: Already using Ansible apt module for package management
- **openssl**: Already using Ansible openssl_* modules for certificate management
- **python3-openssl**: Required for Ansible OpenSSL modules, already specified

### Security Considerations

The repository demonstrates good security practices that should be maintained:
- **SSL/TLS Configuration**: Self-signed certificate generation with proper key management, TLS 1.2 enforcement, SSL protocol hardening
- **File Permissions**: Proper file modes set for certificates (0640) and web content (0644, 0755)
- **SSH Hardening**: InSpec test validates SSH root login restrictions per STIG requirements
- **Vault/secrets management**: 
  - No hardcoded credentials detected in playbooks
  - Certificate keys generated dynamically via OpenSSL modules
  - User credentials in deployment scripts should be moved to Ansible Vault
  - 2 shell scripts contain hardcoded passwords that need vault encryption

### Technical Challenges

This repository faces modernization rather than migration challenges:
- **Deprecated Syntax**: Some tasks use legacy Ansible syntax (e.g., `apt: update_cache=true` should use FQCN `ansible.builtin.apt`)
- **Handler Naming**: Inconsistent handler names between playbooks (`Restart apache` vs `Restart apache2`)
- **Module Updates**: Should migrate to fully qualified collection names (FQCN) for all modules
- **Test Integration**: InSpec tests are external - consider migrating to Ansible's built-in testing with `ansible.builtin.assert`

### Migration Order

Since no actual migration is needed, focus on modernization:
1. **SSL Hardening Playbook** (low risk, simple syntax updates)
2. **Apache HTTPS Playbook** (moderate complexity, multiple module updates needed)
3. **Test Infrastructure** (update Test Kitchen configuration for newer Ansible versions)

### Assumptions

- The repository is intended as a demonstration/example rather than production infrastructure
- Ubuntu 20.04 target is acceptable (could be updated to Ubuntu 22.04 LTS for longer support)
- Self-signed certificates are acceptable for testing (production would need CA-signed certificates)
- The Chef Automate deployment scripts are for test infrastructure setup only
- InSpec integration pattern is intentional for compliance automation demonstration
- No actual Chef cookbooks or recipes exist that need migration to Ansible
- The repository serves as educational content for Chef InSpec + Ansible integration
- Test Kitchen with Vagrant is the preferred testing approach (could consider molecule as alternative)