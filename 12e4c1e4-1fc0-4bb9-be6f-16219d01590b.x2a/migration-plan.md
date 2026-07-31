# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef infrastructure setup scripts and Ansible playbooks with InSpec testing. The repository appears to be primarily educational in nature, demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Chef Automate and Chef Infra Server deployment scripts
2. Existing Ansible playbooks that need to be reviewed and potentially refactored
3. InSpec tests that need to be integrated into the Ansible workflow

Given the limited scope and the fact that part of the codebase is already in Ansible, this migration is estimated to be low complexity and could be completed in 1-2 weeks.

## Module Migration Plan

This repository contains both Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef infrastructure
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https**:
    - Description: Ansible playbook for setting up a secure Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification. Migration should consider integrating with Ansible Molecule for testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality and security. Should be converted to Ansible-compatible testing framework or maintained as InSpec tests.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Either maintain InSpec tests or convert to Ansible-native testing solutions

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and configuration. Migration should maintain or improve security practices:
  - Self-signed certificate generation should be maintained or replaced with Let's Encrypt integration
  - SSL protocol restrictions (disabling SSLv3, enabling TLSv1.2) should be preserved
  - Apache SSL configuration should be maintained

- **Vault/secrets management**:
  - Hardcoded credentials in the setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require understanding of Chef Automate architecture and configuration options. This may require creating custom Ansible roles.
  
- **InSpec Testing Integration**: Determining the best approach for integrating InSpec tests with Ansible workflows. Options include:
  - Keeping InSpec tests and calling them from Ansible
  - Converting InSpec tests to Ansible-native testing solutions
  - Using Molecule with InSpec verifiers

### Migration Order

1. **website-https and poodle-fix playbooks** (low risk, already in Ansible): Review and refactor existing Ansible playbooks to follow best practices
2. **Chef Automate and Chef Server deployment scripts** (moderate complexity): Convert bash scripts to Ansible playbooks
3. **Testing framework** (moderate complexity): Set up Molecule testing to replace Test Kitchen

### Assumptions

1. The repository is primarily educational/demonstrative and not a production codebase
2. The existing Ansible playbooks are functional but may need refactoring to follow best practices
3. InSpec testing is a requirement and should be maintained in some form
4. The Chef Automate and Chef Server deployment is for demonstration purposes and may not need all production-level features
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. No external dependencies or integrations beyond what's visible in the codebase
7. No complex data structures or variables are being used
8. No external inventory or host management is required