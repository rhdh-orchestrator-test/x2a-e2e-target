# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef Automate/Chef Infra Server deployment. The migration scope is relatively small, with only a few components to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format or are simple deployment scripts.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https**:
    - Description: Ansible playbook for deploying a secure website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content verification, SSL protocol verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/README.md`: Documentation for using Chef InSpec with Ansible for compliance automation
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing framework like Molecule with Testinfra or maintain InSpec as a standalone testing tool
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible-compatible configuration management system

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening (poodle_fix.yml) that disables vulnerable protocols and enables TLSv1.2. This should be maintained in the Ansible migration.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider implementing a more robust certificate management solution in the migration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework may require additional effort. Consider using Molecule with Testinfra or maintaining InSpec as a standalone tool.
- **Chef Automate Replacement**: If Chef Automate is being used for compliance reporting, an alternative solution will need to be implemented with Ansible.

### Migration Order

1. **website-https playbook** (already in Ansible format, no migration needed)
2. **poodle-fix playbook** (already in Ansible format, no migration needed)
3. **chef-automate-deployment** (convert Bash scripts to Ansible roles for server deployment)
4. **inspec-tests** (convert to Ansible-compatible testing framework)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, as indicated by the README.md mentioning "working examples" and "how-tos".
2. The Chef InSpec tests are used for compliance verification of the Ansible-deployed website.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment.
4. The hardcoded credentials in the deployment scripts are not used in production environments.
5. The repository does not contain actual Chef cookbooks, only Ansible playbooks and Chef InSpec tests.
6. The migration goal is to convert all components to pure Ansible without any Chef dependencies.