# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and migrating Chef InSpec tests to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require converting to Ansible Molecule or similar testing framework.
- `chef-and-ansible/index.html`: Simple HTML file used as a template for the website. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Ansible assertions for simpler tests
  - Option 3: Maintain InSpec as a separate testing tool but integrate with Ansible workflow

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation management
  - AWX (open source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for pipeline integration

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS configuration is maintained in the migrated Ansible roles.
  - Migration approach: Create an Ansible role for Apache with SSL that follows current security best practices.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create Ansible tasks to enforce the same SSH security controls and use Ansible assertions or Molecule tests to verify compliance.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault.
  - Self-signed certificates should be managed securely, potentially using Ansible Vault for private keys.
  - Count of credentials detected: 3 (username, password, and SSL private key)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing approaches.
  - Mitigation: Use Ansible Molecule with testinfra which has similar syntax to InSpec.

- **Chef Automate/Server Replacement**: Finding equivalent functionality in Ansible ecosystem.
  - Mitigation: Evaluate Ansible Automation Platform or AWX as replacements, focusing on the specific features used in the current Chef implementation.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible): Convert to Ansible role with proper structure
2. **poodle_fix playbook** (low risk, already in Ansible): Convert to Ansible role or include in the Apache role
3. **InSpec tests** (moderate complexity): Convert to Ansible Molecule tests
4. **Chef Automate/Server deployment scripts** (high complexity): Replace with Ansible Automation Platform or AWX deployment

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README.md mentioning "working examples" and "how-tos".
2. The Chef InSpec tests are used for compliance validation of infrastructure deployed by Ansible, not for validating Chef-managed infrastructure.
3. The setup-automate scripts are used for setting up a Chef environment for testing or demonstration, not for production use.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure alternatives in a production environment.
5. The migration will maintain the same functionality but improve structure and security practices.
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.