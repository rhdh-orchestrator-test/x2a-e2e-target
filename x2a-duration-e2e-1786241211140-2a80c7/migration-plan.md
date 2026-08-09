# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef automation scripts that need to be consolidated into a unified Ansible approach. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, along with some Chef server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef-related scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule for infrastructure testing and compliance verification
- **Test Kitchen**: Replace with Ansible-native testing frameworks like Molecule
- **Chef Automate/Server**: Evaluate if these components are needed or if they can be replaced with Ansible Tower/AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should include equivalent Ansible tasks to enforce these security practices.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly but should be managed securely in production

### Technical Challenges

- **InSpec Tests**: Converting InSpec tests to equivalent Ansible verification methods will require careful mapping of test assertions
- **Chef Server Deployment**: If Chef Server is still needed, creating equivalent Ansible roles for deployment and configuration

### Migration Order

1. `website_https.yml` (already Ansible, low risk)
2. `poodle_fix.yml` (already Ansible, low risk)
3. InSpec tests conversion to Ansible-compatible testing framework
4. Chef server deployment scripts conversion to Ansible roles

### Assumptions

1. The repository is primarily for demonstration purposes showing how Chef InSpec can work with Ansible
2. The Chef server deployment scripts are examples and not production-critical
3. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
4. The security configurations are examples and may need enhancement for production use
5. No external dependencies or complex integrations are present beyond what's visible in the repository
6. The migration goal is to consolidate everything to pure Ansible without Chef components
7. No actual Chef cookbooks or recipes are present in the repository that need migration