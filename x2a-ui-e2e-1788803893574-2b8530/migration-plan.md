# MIGRATION FROM CHEF INSPEC EXAMPLES TO ANSIBLE

This repository contains Chef InSpec testing examples integrated with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks with Chef InSpec compliance verification, representing a hybrid approach that demonstrates how Chef InSpec can complement Ansible automation. Migration complexity is minimal as the core automation is already implemented in Ansible.

## Module Migration Plan

This repository contains example configurations demonstrating Chef InSpec integration with Ansible:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Apache HTTPS web server configuration with SSL/TLS security hardening and compliance verification using Chef InSpec
- Path: chef-and-ansible/
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Apache 2.4 installation, self-signed SSL certificate generation, virtual host configuration, POODLE vulnerability mitigation, compliance testing for HTTPS and SSH security

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `website_https.yml`: Main Ansible playbook for Apache HTTPS setup with SSL certificate management
- `poodle_fix.yml`: Security hardening playbook to disable SSLv3 and enforce TLS 1.2
- `index.html`: Static HTML content for web server testing
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG control)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with native Ansible testing modules (ansible.builtin.uri, ansible.builtin.command) or integrate with external testing frameworks
- **Test Kitchen**: Replace with Ansible Molecule for testing and verification workflows
- **Vagrant**: Continue using Vagrant or migrate to container-based testing with Docker

### Security Considerations

- **SSL/TLS Configuration**: Current implementation uses self-signed certificates for testing; production migration should integrate with proper certificate management (Let's Encrypt, internal CA)
- **Compliance Testing**: InSpec security profiles need migration to Ansible-native compliance checking or integration with external compliance tools
- **SSH Hardening**: SSH security configurations are tested but not implemented in the playbooks; migration should include SSH hardening tasks
- **Credential Management**: No hardcoded credentials detected in current implementation; maintain this security posture in migrated solution

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-native testing requires rewriting compliance checks using Ansible modules or integrating alternative testing tools
- **Compliance Automation**: STIG controls and security profiles need mapping to Ansible security roles or custom compliance modules
- **Continuous Verification**: Current InSpec integration provides ongoing compliance monitoring; replacement solution needs similar continuous verification capabilities

### Migration Order

1. **Apache HTTPS Module** (low complexity - already in Ansible format)
2. **Security Hardening Module** (moderate complexity - extend existing poodle_fix.yml)
3. **Compliance Testing Framework** (high complexity - replace InSpec with Ansible-native testing)

### Assumptions

- The repository serves as example/demonstration code rather than production infrastructure requiring migration
- Current Ansible playbooks are functional and represent the desired end state for automation
- Chef InSpec testing provides value that should be preserved in the migrated solution through alternative testing approaches
- Test Kitchen workflow should be replaced with Ansible Molecule for consistency with Ansible ecosystem
- Production deployment would require proper certificate management beyond self-signed certificates
- SSH hardening implementation is missing from current playbooks but is tested via InSpec profiles
- The setup-automate scripts are deployment utilities rather than configuration management requiring migration