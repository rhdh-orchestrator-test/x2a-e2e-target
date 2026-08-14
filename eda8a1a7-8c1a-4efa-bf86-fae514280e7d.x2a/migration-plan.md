# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef server setup scripts that need to be migrated to a consistent Ansible-based approach. The repository appears to be a demonstration of using Chef InSpec for compliance testing with Ansible playbooks, along with scripts for setting up Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which are already in Ansible format) and medium complexity for the Chef server setup scripts.

## Module Migration Plan

This repository contains Ansible playbooks and Chef server setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a separate testing tool
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible-based configuration management solution

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Migration should ensure this security check is maintained.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **InSpec Testing**: The repository uses InSpec for compliance testing. Migration should either maintain InSpec or replace it with equivalent Ansible-native testing.
- **Chef Server Setup**: The Chef server setup scripts need to be converted to Ansible playbooks, which requires understanding of Chef server architecture.
- **Test Kitchen Integration**: The Test Kitchen configuration needs to be replaced with Molecule or another Ansible-native testing framework.

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
2. **poodle-fix playbook** (low risk, already in Ansible format)
3. **InSpec tests** (medium risk, requires conversion to Ansible-native testing)
4. **Chef server setup scripts** (high complexity, requires conversion from bash/Chef to Ansible)

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. InSpec tests may need to be converted to Ansible-native testing solutions
3. The Chef server setup scripts are used for demonstration purposes and not production
4. The hardcoded credentials in the setup scripts are for demonstration only
5. The repository is primarily for educational purposes as indicated by the README
6. The target environment is Ubuntu 20.04 as specified in kitchen.yml
7. The migration should maintain the same functionality and security posture
8. No external dependencies or integrations beyond what's visible in the repository