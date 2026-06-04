# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Sample HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native solutions:
  - For compliance testing: Use Ansible Lint for static analysis
  - For runtime verification: Convert InSpec tests to Ansible assert modules or use ansible.builtin.shell with grep/awk
  - Alternative: Integrate with Ansible Molecule for testing

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Ensure the Ansible task that sets SSLProtocol to "-all +TLSv1.2" is preserved
  
- **SSH Security**: The InSpec test for SSH root login must be converted to Ansible
  - Approach: Create an Ansible task that checks the sshd_config file for PermitRootLogin setting

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Approach: Maintain the openssl_* modules usage in Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible verification
  - Mitigation: Use Ansible's assert module combined with command/shell modules to perform similar checks
  - Example: Replace `describe port(443) { it { should be_listening } }` with Ansible's `wait_for` module

- **Chef Automate Deployment**: Converting Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef Automate and Chef Server deployment
  - Consider whether Chef Automate is still needed if fully migrating to Ansible

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Automate Deployment Scripts** (high complexity, requires decision on whether to maintain Chef infrastructure)

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies
2. The InSpec tests need to be converted to equivalent Ansible verification tasks
3. The Chef Automate and Chef Server deployment may no longer be needed if fully migrating to Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The security requirements (TLS 1.2, SSH hardening) must be maintained in the migrated solution
6. Test Kitchen will be replaced with Ansible Molecule or another Ansible-native testing framework