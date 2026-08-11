# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Chef InSpec tests that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be replaced with Ansible automation
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

Based on the repository analysis, this is a low-complexity migration that could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

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
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks

- **automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static HTML file used in the website deployment. Can be directly used in Ansible without changes.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible assert modules for inline testing
  - Option 3: Maintain InSpec as a separate testing tool but invoke it from Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation management:
  - Option 1: Migrate to AWX/Ansible Tower for web UI and job scheduling
  - Option 2: Use GitLab CI/CD or Jenkins with Ansible for automation
  - Option 3: Use simple Git repository with ansible-pull for configuration management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible:
  - Migrate the OpenSSL certificate generation to Ansible's crypto modules
  - Consider using Let's Encrypt integration for production environments
  - Maintain the TLS 1.2 requirement and disabled SSL3 as in the current configuration

- **SSH Security**: The InSpec tests verify SSH root login is disabled:
  - Implement equivalent checks using Ansible's assert module or Molecule/Testinfra
  - Consider expanding SSH hardening using the ansible-hardening role

- **Credentials Management**: 
  - The deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Identified credentials: 1 user password in each deployment script

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Challenge: InSpec has a domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use Testinfra with Molecule which provides similar testing capabilities with Python syntax

- **Chef Server Replacement**: Replacing Chef Server functionality:
  - Challenge: Chef Server provides centralized configuration management that needs an equivalent in Ansible
  - Mitigation: Implement AWX/Ansible Tower or use GitLab CI/CD with Ansible for similar functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need refactoring to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, requires conversion to Ansible testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires complete rewrite as Ansible playbooks

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production, based on the README content
2. The InSpec tests are used alongside Ansible for compliance verification rather than as part of a larger Chef ecosystem
3. The deployment scripts are used for setting up test environments rather than production Chef infrastructure
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The Test Kitchen configuration is used for local testing and development rather than CI/CD pipelines