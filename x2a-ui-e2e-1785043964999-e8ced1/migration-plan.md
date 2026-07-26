# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need to be migrated to a unified Ansible solution. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, along with scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for this migration is 1-2 weeks, with low complexity for the Ansible playbooks (which are already in Ansible format) and medium complexity for the Chef server deployment scripts (which need to be converted to Ansible roles).

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS website deployment
- `chef-and-ansible/index.html`: Likely a static HTML file for the website example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX for centralized automation management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained in the migrated Ansible roles.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing Let's Encrypt integration for production environments.
- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials that should be replaced with Ansible Vault or another secrets management solution:
  - Username/password in deploy-automate.sh and deploy-chef-server.sh
  - Count: 2 credential sets (one in each deployment script)

### Technical Challenges

- **Chef-specific Functionality**: The Chef Automate and Chef Infra Server deployment scripts perform Chef-specific operations that need to be reimplemented in Ansible:
  - Mitigation: Create Ansible roles that install and configure equivalent functionality or integrate with existing Chef infrastructure
  
- **InSpec Testing**: The repository demonstrates InSpec testing with Ansible, which needs to be replaced with Ansible-native testing:
  - Mitigation: Use Ansible Molecule for infrastructure testing or integrate with other testing frameworks

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
2. **poodle_fix playbook** (low risk, already in Ansible format)
3. **Chef deployment scripts** (medium complexity, requires conversion to Ansible roles)

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment.
2. The Chef InSpec tests are used for compliance verification and will need equivalent functionality in the Ansible solution.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
4. The target environment is Ubuntu 20.04, but the solution should be adaptable to other Linux distributions.
5. The migration will maintain the same functionality but standardize on Ansible as the configuration management tool.
6. The Chef Automate and Chef Infra Server functionality may be replaced with Ansible Automation Platform or AWX, depending on requirements.