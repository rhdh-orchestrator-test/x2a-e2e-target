# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verification**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh-security-profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled according to security standards
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checking with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module with appropriate checks
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Molecule for Ansible role testing, which provides similar functionality but is more Ansible-native

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are correctly migrated
  - Maintain the security posture by disabling vulnerable protocols

- **SSH Security Controls**: The SSH security profile must be converted to equivalent Ansible assertions
  - Preserve the STIG compliance references and documentation
  - Maintain the security validation logic for SSH root login

- **Certificate Management**: Self-signed certificate generation must be preserved
  - The openssl_* modules are already Ansible-native and can be kept as-is

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's intent
  - For complex tests, consider using the community.general.assert module which offers more flexibility

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Challenge: The scripts use Chef-specific CLI tools that need Ansible alternatives
  - Mitigation: Research if there are existing Ansible roles for Chef server deployment, or create custom roles

### Migration Order

1. **website-https and poodle-fix playbooks** (low risk, already in Ansible)
   - Review and ensure they follow Ansible best practices
   - Convert to roles if appropriate for better organization

2. **InSpec tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions with appropriate documentation

3. **Chef deployment scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functioning correctly and don't require significant changes beyond potential conversion to roles.

2. The primary goal is to eliminate Chef InSpec dependency while maintaining equivalent testing capabilities.

3. The deployment scripts for Chef Automate and Chef Server are intended to be converted to Ansible rather than preserved as-is.

4. The target environment will continue to be Ubuntu 20.04 or compatible systems.

5. There are no external dependencies or integrations not visible in the provided repository.

6. The security compliance requirements (STIG references) in the SSH profile need to be preserved in the Ansible implementation.

7. Test Kitchen is used only for development/testing and not in production pipelines that would require migration.