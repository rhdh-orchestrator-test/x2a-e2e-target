# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks that set up a secure web server
3. Integrating Chef InSpec tests into an Ansible-based testing framework

The migration complexity is **LOW** as most of the repository already contains Ansible playbooks. The estimated timeline for migration is **1-2 weeks** for a single developer, focusing primarily on converting the Chef server deployment scripts to Ansible and ensuring the InSpec tests continue to work with the new deployment method.

## Module Migration Plan

This repository contains a mix of Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts that install Chef components
    - Key Features: User creation, organization setup, Chef server configuration

- **secure-web-server**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-vulnerability-fix**:
    - Description: Ansible playbook to fix POODLE SSL vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLS 1.2

- **compliance-testing**:
    - Description: Chef InSpec tests for validating web server and SSH security
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, SSH root login testing

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for web server testing
- `README.md`: Documentation files explaining the repository purpose

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with alternative configuration management approach using Ansible
- **Chef InSpec**: Maintain as a testing tool or replace with Ansible-native alternatives:
  - Option 1: Continue using InSpec with Ansible (recommended for complex compliance testing)
  - Option 2: Replace with Ansible assert modules and community.general.test modules

### Security Considerations

- **SSL Configuration**: Maintain the SSL hardening in the migration, ensuring TLS 1.2 is enforced
- **SSH Hardening**: Preserve the SSH security controls that disable root login
- **Self-signed Certificates**: Consider replacing with Let's Encrypt integration for production environments
- **Credentials in Scripts**: The current scripts contain hardcoded passwords that should be moved to Ansible Vault

### Technical Challenges

- **Chef Server Replacement**: Determining the appropriate Ansible-based alternative to Chef Server functionality
  - Mitigation: Consider AWX/Ansible Tower or other Ansible-based configuration management platforms
- **InSpec Test Integration**: Ensuring InSpec tests continue to work with the new Ansible deployment
  - Mitigation: Use Ansible's built-in support for InSpec or migrate to Ansible-native testing

### Migration Order

1. **secure-web-server** (already Ansible, no migration needed)
2. **ssl-vulnerability-fix** (already Ansible, no migration needed)
3. **chef-automate-deployment** (convert Bash scripts to Ansible playbooks)
4. **compliance-testing** (integrate InSpec tests with Ansible or convert to Ansible-native tests)

### Assumptions

1. The primary goal is to eliminate Chef server/Automate dependencies while maintaining the existing functionality
2. InSpec tests are valuable and should be preserved or converted to equivalent functionality
3. The existing Ansible playbooks are working correctly and don't need significant modifications
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The deployment will continue to use self-signed certificates for development/testing
6. The current security hardening requirements (TLS 1.2, SSH restrictions) must be maintained