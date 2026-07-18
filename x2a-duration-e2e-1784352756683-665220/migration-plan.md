# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with equivalent Ansible roles and playbooks. The estimated timeline for this migration is 1-2 weeks, with most of the effort focused on creating Ansible roles for Chef server functionality.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **apache-https-website**:
    - Description: Ansible playbook for configuring Apache with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **inspec-compliance-tests**:
    - Description: InSpec tests for verifying HTTPS website and SSH configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol verification, SSH security compliance

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the Chef InSpec with Ansible examples
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server
- `README.md`: Main repository documentation

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **InSpec**: Maintain InSpec for compliance testing, but integrate with Ansible using the `ansible.builtin.shell` module or consider migrating to Ansible's built-in assert module or Molecule for testing

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL hardening (disabling SSLv3, enabling TLSv1.2) that must be preserved in the migrated Ansible playbooks
- **SSH Hardening**: InSpec tests verify SSH root login is disabled, which should be enforced in the migrated Ansible playbooks
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - SSL certificates and keys generated and stored in `/etc/apache2/certs/`
  - Recommend replacing hardcoded credentials with Ansible Vault

### Technical Challenges

- **Chef Automate Deployment**: Creating an equivalent Ansible role for Chef Automate deployment will require careful mapping of the bash script functionality to Ansible tasks
- **InSpec Integration**: Determining the best approach for integrating InSpec tests with Ansible (options include using the `shell` module to run InSpec directly or migrating tests to Ansible's native testing capabilities)
- **Test Kitchen**: Replacing Test Kitchen with an Ansible-native testing framework like Molecule

### Migration Order

1. **apache-https-website** (low risk, already in Ansible format)
2. **chef-automate-deployment** (moderate complexity, requires creating new Ansible roles)
3. **inspec-compliance-tests** (high complexity, requires integration strategy)

### Assumptions

1. The primary goal is to consolidate all configuration management into Ansible, eliminating the need for Chef Automate and Chef Infra Server
2. InSpec tests should be preserved for compliance verification, either by calling them from Ansible or by migrating them to equivalent Ansible tests
3. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
4. The Apache HTTPS website configuration is representative of the production environment
5. No additional Chef cookbooks or recipes exist beyond what is visible in the repository
6. The hardcoded credentials in the deployment scripts are for testing purposes only and will be replaced with secure credential management in production
7. The migration will maintain the same level of security hardening present in the original configuration