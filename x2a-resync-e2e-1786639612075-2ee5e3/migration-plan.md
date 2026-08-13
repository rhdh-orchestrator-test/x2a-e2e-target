# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef automation scripts that need to be consolidated into a unified Ansible approach. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, as well as containing Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for migration is 1-2 weeks given the limited scope.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec test profile for SSH security compliance checks
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing framework or integrate with Molecule for testing
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Evaluate if these components need to be replaced with Ansible Tower/AWX or if they can be eliminated entirely

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. This configuration should be preserved in the migrated Ansible playbooks.
- **SSH Hardening**: The InSpec tests check for SSH root login being disabled. This security check should be implemented in the migrated Ansible playbooks.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing Let's Encrypt integration for production environments.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec Testing**: The repository relies on Chef InSpec for compliance testing. The migration will need to address how to maintain compliance testing within an Ansible-only environment.
  - Mitigation: Consider using Ansible's built-in assert module or integrating with Molecule for testing
  
- **Chef Automate Deployment**: The bash scripts for deploying Chef Automate and Chef Infra Server will need to be completely rewritten as Ansible playbooks.
  - Mitigation: Create equivalent Ansible roles for server provisioning and configuration

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, requires complete rewrite as Ansible roles)

### Assumptions

1. The repository is primarily a demonstration of how Chef InSpec can work alongside Ansible, rather than a production environment.
2. The Chef deployment scripts are used for setting up test environments rather than production Chef infrastructure.
3. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
4. There is no requirement to maintain backward compatibility with Chef components after migration.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and not used in production.
6. The self-signed certificates are acceptable for the use case, but production environments might require proper CA-signed certificates.