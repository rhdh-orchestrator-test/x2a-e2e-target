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
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing the web server. Can be preserved as-is or included as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For website_https_verify.rb: Use Ansible's uri module with assert for HTTP checks and community.crypto.openssl_certificate_info module for SSL verification
  - For ssh_profile.rb: Use Ansible's assert module with lineinfile or template module to verify SSH configuration

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in poodle_fix.yml that disables SSLv3 and enables only TLSv1.2
- **SSH Security**: The SSH root login check in ssh_profile.rb must be preserved in the Ansible equivalent
- **Credentials Management**: 
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected (username/password in both deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions will require careful mapping of test functionality
  - Mitigation: Use Ansible's assert module combined with command/shell modules to run equivalent checks
  
- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible requires understanding of Chef Automate's installation process
  - Mitigation: Use Ansible's get_url module to download Chef Automate CLI and command module to execute the deployment with appropriate parameters

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already in Ansible format, no migration needed
2. **InSpec Tests**: Convert to Ansible assertions or Ansible-compatible testing framework
   - website_https_verify.rb
   - ssh_profile.rb
3. **Deployment Scripts**: Convert to Ansible playbooks
   - deploy-chef-server.sh
   - deploy-automate.sh
4. **Testing Framework**: Replace Test Kitchen with Molecule

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification
2. The InSpec tests are currently used for validation and compliance checking, and this functionality needs to be preserved
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. No external dependencies or integrations beyond what's visible in the repository
6. The migration is primarily focused on replacing Chef InSpec with Ansible-native testing while preserving the existing Ansible playbooks
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution