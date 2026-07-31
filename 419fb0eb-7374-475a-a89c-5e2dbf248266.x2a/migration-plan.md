# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

The complexity is moderate, with most of the work focused on converting InSpec tests to an Ansible-compatible testing framework. The estimated timeline for migration is 2-3 weeks, with the majority of time spent on test conversion and validation.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static HTML file used in the website deployment. No migration needed, can be used as-is in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for infrastructure testing
  - Option 3: Maintain InSpec as a standalone testing tool but invoke from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Consider using Ansible Collections for role organization

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible:
  - Use Ansible Vault for storing sensitive certificate information
  - Consider integrating with certificate management systems

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained:
  - Convert SSH security tests to Ansible-compatible tests
  - Implement SSH hardening using Ansible security roles

- **Credentials in Scripts**: The deployment scripts contain hardcoded credentials:
  - Replace with Ansible Vault for secure credential storage
  - Use variable files for environment-specific configurations

- **Vault/secrets management**:
  - Hardcoded credentials found in setup-automate scripts (username, password)
  - SSL certificates generated and managed in website_https.yml

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - InSpec has specific resource types that may not have direct equivalents
  - Solution: Map InSpec resources to Testinfra or Goss checks, maintaining test coverage

- **Compliance Reporting**: Chef InSpec provides compliance reporting capabilities:
  - Solution: Integrate with compliance tools like OpenSCAP or maintain InSpec as a standalone tool called from Ansible

- **Chef Server Migration**: Moving from Chef Server to Ansible management:
  - Solution: Use Ansible AWX/Tower for web UI and job scheduling
  - Implement proper inventory management to replace Chef Server node management

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Add documentation and improve variable usage
   - Implement Ansible best practices (roles, handlers, etc.)

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible-compatible testing framework
   - Validate test coverage and functionality
   - Integrate with CI/CD pipeline

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Create Ansible playbooks to replace bash scripts
   - Implement secure credential management
   - Test deployment in isolated environment

### Assumptions

1. The repository is primarily used for demonstration and educational purposes, not production deployments
2. The InSpec tests are used for compliance validation of infrastructure
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data structures or state management requirements
7. No custom Chef resources or complex Chef-specific functionality
8. The migration is focused on functionality, not necessarily preserving the exact structure of the original repository