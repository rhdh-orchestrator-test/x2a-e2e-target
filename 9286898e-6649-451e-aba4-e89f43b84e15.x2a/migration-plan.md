# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests and Ansible playbooks demonstrating integration patterns, rather than traditional Chef cookbooks requiring migration. The primary migration focus is on consolidating the compliance testing approach within a pure Ansible ecosystem while preserving the security validation capabilities currently provided by Chef InSpec.

## Module Migration Plan

This repository contains demonstration content that showcases Chef InSpec integration with Ansible rather than production Chef cookbooks:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating HTTPS website deployment with Apache, SSL certificate generation, and security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Self-signed SSL certificates, Apache virtual host configuration, security compliance validation via InSpec

**poodle-vulnerability-fix**:
- Description: Ansible playbook for SSL/TLS protocol hardening to address POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG-based controls)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible compliance modules (ansible.posix.firewalld, community.crypto.openssl_certificate validation, etc.)
- **Test Kitchen**: Migrate to Molecule for Ansible playbook testing and validation
- **Chef Automate/Server**: Replace with Ansible AWX/Tower for centralized automation and compliance reporting

### Security Considerations

- **SSL/TLS Certificate Management**: Current implementation uses self-signed certificates via Ansible crypto modules - production migration should integrate with proper CA or Let's Encrypt
- **SSH Hardening Compliance**: InSpec SSH profile enforces STIG controls - migrate to Ansible security role with equivalent hardening tasks
- **Apache Security Configuration**: SSL protocol restrictions and virtual host security settings need validation through Ansible assert modules
- **Credential Management**: Deployment scripts contain hardcoded passwords - implement Ansible Vault for secrets management

### Technical Challenges

- **InSpec Test Translation**: Converting Ruby-based InSpec controls to Ansible assert tasks or Molecule verifiers requires rewriting test logic
- **Compliance Reporting**: Chef InSpec provides detailed compliance reporting - need equivalent reporting mechanism in pure Ansible environment
- **Test Kitchen Integration**: Current workflow uses Test Kitchen for infrastructure testing - migration to Molecule requires workflow adaptation
- **STIG Compliance Validation**: SSH profile implements specific STIG controls - ensure equivalent security validation in Ansible-native approach

### Migration Order

1. **Ansible Playbook Validation** (already complete - playbooks are native Ansible)
2. **InSpec Test Migration** (convert Ruby tests to Ansible assert tasks or Molecule verifiers)
3. **Test Infrastructure Migration** (replace Test Kitchen with Molecule for testing workflow)
4. **Compliance Reporting Setup** (implement Ansible-native compliance reporting to replace InSpec output)

### Assumptions

- This repository serves as a demonstration/example rather than production infrastructure requiring migration
- The Ansible playbooks are already functional and represent the target state
- InSpec tests provide the compliance requirements that must be preserved in the migration
- Test Kitchen workflow represents the desired testing approach that should be replicated with Ansible-native tools
- Chef Automate deployment scripts are for demonstration purposes and not part of the core migration scope
- Ubuntu 20.04 target platform will be maintained in the migrated solution
- Self-signed certificate approach is acceptable for demonstration purposes but would require proper CA integration for production use
- The migration priority is on preserving compliance validation capabilities rather than infrastructure provisioning (since Ansible playbooks already exist)