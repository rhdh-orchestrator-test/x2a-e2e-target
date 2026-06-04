# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

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
    - Description: Chef InSpec control that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For website_https_verify.rb: Use Ansible's uri module and assert module for HTTP checks
  - For SSL protocol verification: Use Ansible's community.crypto.openssl_certificate_info module
  - For ssh_profile.rb: Use Ansible's lineinfile or template module to check SSH configuration

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Preserve the existing Ansible task that disables SSLv3 and enables TLSv1.2
  
- **SSH Security**: Maintain the SSH root login restriction check
  - Approach: Convert the InSpec control to an Ansible task that checks the sshd_config file

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible assert module combined with uri module for HTTP checks
  - For more complex tests, consider using the ansible.builtin.shell module to run openssl commands and validate the output

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef Automate and Chef Infra Server deployment
  - Use Ansible's package, service, and command modules to handle the installation and configuration

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible tests
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible roles

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't need significant modifications
2. The InSpec tests are currently used for validation and compliance checking, and this functionality needs to be preserved
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which may be replaced with an Ansible-based solution
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. The migration doesn't require changes to the underlying application functionality, just the automation tooling
6. No external dependencies or integrations beyond what's visible in the repository
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution