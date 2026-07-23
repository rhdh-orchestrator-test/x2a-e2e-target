# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server setup scripts. The primary migration focus will be on standardizing all infrastructure as code to Ansible. The repository appears to be a demonstration of using Chef InSpec for compliance testing with Ansible playbooks, along with scripts for setting up Chef infrastructure.

The migration complexity is **LOW to MEDIUM** as the repository contains only a few Ansible playbooks and shell scripts. The estimated timeline for migration is **1-2 weeks** for a single developer, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for security compliance

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user creation, organization setup

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user creation, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration
- `index.html`: Likely a static HTML file for the website example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on any cloud or on-premises VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Consider using Ansible's built-in inventory for simpler testing scenarios

### Security Considerations

- **SSL/TLS Configuration**: The current playbooks enforce TLSv1.2 and disable older protocols. This security practice should be maintained in the migrated Ansible playbooks.
  
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider:
  - Maintaining this approach for development/testing
  - Adding support for Let's Encrypt for production environments
  - Using Ansible Vault for storing certificate information securely

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected (in both setup scripts)

### Technical Challenges

- **Chef InSpec Testing**: The current setup uses Chef InSpec for compliance testing. Migration options:
  - Keep InSpec as a standalone tool called from Ansible
  - Replace with Ansible-native testing solutions
  - Use Molecule with testinfra for similar functionality

- **Chef Server Setup**: The Chef server setup scripts need to be converted to Ansible playbooks:
  - Challenge: Ensuring idempotent installation of Chef components
  - Solution: Use Ansible's package management and service modules with appropriate state checks

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Add proper idempotency checks
   - Implement Ansible best practices (roles, variables)

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https as a role or included task

3. **Chef Server Setup Scripts** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper variable management with Ansible Vault
   - Add idempotency checks

4. **Testing Framework** (high complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native testing)
   - Implement chosen testing framework
   - Ensure all existing tests are migrated

### Assumptions

1. The repository is primarily for demonstration purposes, showing how Chef InSpec can be used with Ansible.
2. The actual infrastructure being managed is relatively simple (web servers with HTTPS).
3. There are no complex Chef cookbooks or recipes that need migration (only setup scripts).
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
5. The hardcoded credentials in the setup scripts are for demonstration purposes only.
6. The Test Kitchen configuration is used for testing the Ansible playbooks with InSpec.
7. There may be additional files or dependencies not visible in the repository structure.
8. The migration goal is to standardize on Ansible while maintaining the same functionality.