# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the website deployment example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For website_https_verify.rb: Use Ansible's uri module and assert module to verify HTTPS functionality
  - For ssh_profile.rb: Use Ansible's assert module with lineinfile or template module to verify SSH configuration

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Preserve the existing Ansible task that disables SSLv3 and enables only TLSv1.2

- **SSH Security**: The migration must maintain the SSH security controls verified by the InSpec test
  - Approach: Create an Ansible task to ensure PermitRootLogin is not set to 'yes' in sshd_config

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module combined with command, uri, and other modules to replicate InSpec functionality
  - Consider using ansible-lint for static analysis of playbooks

- **Chef Automate Deployment**: Converting Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef Automate and Chef Infra Server deployment
  - Use Ansible's package, command, and template modules to replicate the bash script functionality

### Migration Order

1. Preserve existing Ansible playbooks (website_https.yml, poodle_fix.yml) - low risk
2. Convert InSpec tests to Ansible assertions (website_https_verify.rb, ssh_profile.rb) - moderate complexity
3. Convert Chef deployment scripts to Ansible playbooks (deploy-automate.sh, deploy-chef-server.sh) - moderate complexity
4. Replace Test Kitchen with Ansible Molecule - moderate complexity

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need significant changes
2. The repository is primarily used for demonstration purposes rather than production deployment
3. The InSpec tests are used for validation only and not for continuous compliance monitoring
4. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments
5. There are no additional Chef cookbooks or recipes that need migration beyond what's visible in the repository
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
7. The migration doesn't need to address scaling or high availability concerns
8. No external integrations or APIs are being used that would require special handling