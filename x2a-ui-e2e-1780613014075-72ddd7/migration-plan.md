# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Implement Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Keep InSpec as a standalone tool if preferred

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS settings are maintained during migration.
  - Migration approach: Preserve the TLSv1.2 requirement and disabled SSLv3 configuration
  
- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Implement equivalent checks using Ansible's assert module or Molecule

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed SSL certificates generated during deployment
  - Migration approach: Replace hardcoded credentials with Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions may require different approaches:
  - Challenge: InSpec provides specialized resources for testing (port, http, ssl) that don't have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible's uri module, wait_for module, and shell commands with assert to achieve similar testing capabilities

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible:
  - Challenge: The scripts perform specific Chef-related operations that need to be replicated in Ansible
  - Mitigation: Create Ansible roles that perform equivalent operations using the command module where necessary

### Migration Order

1. **website_https playbook** (already in Ansible, no migration needed)
2. **poodle_fix playbook** (already in Ansible, no migration needed)
3. **InSpec tests** (convert to Ansible testing framework)
4. **Chef deployment scripts** (convert to Ansible playbooks)

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies and move to a pure Ansible solution
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification
3. The deployment scripts for Chef Automate and Chef Infra Server are to be converted to Ansible, not kept as-is
4. The security requirements (SSL/TLS versions, SSH configuration) must be maintained in the migrated solution
5. Test Kitchen is used only for development/testing and not in production
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives
7. The target environment will continue to be Ubuntu 20.04 or compatible systems