# MIGRATION FROM CHEF AND BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks, along with Bash scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks and standardizing the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec_tests**:
    - Description: Chef InSpec tests for validating HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, SSH root login security check

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for infrastructure testing
  - Option 2: Use ansible-test with Docker or Vagrant drivers

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower
  - Option 2: Use Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration maintains:
  - Proper certificate generation
  - Secure protocol settings (TLSv1.2)
  - Disabled vulnerable protocols (SSLv3)

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure:
  - SSH hardening is maintained in the Ansible equivalent
  - Compliance testing is implemented for SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 sets of credentials in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Challenge: InSpec has specific syntax for compliance testing
  - Mitigation: Use ansible-lint and custom modules to replicate InSpec functionality

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible:
  - Challenge: The scripts install Chef-specific components
  - Mitigation: Create Ansible roles to replace Chef Automate/Infra Server or migrate to Ansible Automation Platform

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Standardize according to Ansible best practices
   - Implement idempotency improvements
   - Fix HTML syntax error in webtext variable

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Standardize according to Ansible best practices
   - Fix handler name inconsistency (Restart apache2 vs Restart apache)

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-compatible testing framework
   - Implement equivalent checks for HTTPS and SSH security

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible roles and playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks are functional but may need standardization
2. The InSpec tests are used for compliance validation after deployment
3. The Chef Automate and Chef Infra Server deployments are for infrastructure management that will be replaced by Ansible
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. There are no external dependencies or integrations not visible in the repository
6. The hardcoded credentials in the deployment scripts are examples and not production credentials
7. The migration will maintain the same level of security compliance testing
8. The HTML content in the website_https.yml playbook has a syntax error that should be fixed during migration