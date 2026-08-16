# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests as they are already compatible with Ansible

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains bash scripts and Ansible playbooks that need individual migration planning:

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
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen with Ansible**: Maintain but update to use pure Ansible testing approach
- **InSpec**: Maintain as is, as InSpec works well with Ansible for compliance testing

### Security Considerations

- **SSH Root Login**: The InSpec tests verify that SSH root login is disabled, which should be maintained in the Ansible configuration
- **SSL/TLS Configuration**: The playbooks enforce TLS 1.2 and disable SSL3 to mitigate POODLE vulnerability
- **Self-signed Certificates**: The playbooks generate self-signed certificates, which should be replaced with proper certificate management
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - No encryption or secure credential management in the current implementation
  - Migration should implement Ansible Vault for securing credentials

### Technical Challenges

- **Chef Automate/Infra Server Deployment**: Converting the bash scripts to Ansible playbooks will require understanding of Chef Automate architecture and deployment requirements
  - Mitigation: Create dedicated Ansible roles for Chef Automate and Chef Infra Server deployment
  
- **InSpec Integration**: Ensuring that InSpec tests continue to work with the new Ansible implementation
  - Mitigation: Maintain the existing InSpec tests and update the Ansible playbooks to ensure they meet the compliance requirements

- **Configuration Parameters**: Ensuring all configuration parameters from the bash scripts are properly translated to Ansible variables
  - Mitigation: Create a comprehensive variable file that maps all configuration parameters from the bash scripts

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already in Ansible format)
   - Refactor `website_https.yml` and `poodle_fix.yml` to follow Ansible best practices
   - Update variable handling and implement Ansible Vault for secrets

2. **Chef Deployment Scripts** (Moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement variable files to replace hardcoded values in bash scripts

3. **Testing Framework** (Low complexity)
   - Update Test Kitchen configuration to work with the new Ansible implementation
   - Ensure InSpec tests continue to work with the migrated playbooks

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the README.md
2. The Chef deployment scripts are used for setting up Chef infrastructure, not for actual configuration management
3. The existing Ansible playbooks are already in a format that can be used in production
4. The InSpec tests are used for compliance verification and should be maintained
5. No complex data structures or external dependencies are used in the current implementation
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. No specific cloud provider requirements are present
8. No complex networking or firewall configurations are needed
9. The migration is focused on converting the bash scripts to Ansible and improving the existing Ansible playbooks