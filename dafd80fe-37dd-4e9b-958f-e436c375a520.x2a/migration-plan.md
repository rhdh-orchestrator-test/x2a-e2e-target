# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef server setup scripts and Ansible playbooks that are used for demonstration purposes. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance automation. The repository does not contain traditional Chef cookbooks but rather contains:

1. Shell scripts for deploying Chef Automate and Chef Infra Server
2. Ansible playbooks for configuring web servers with HTTPS
3. InSpec tests for verifying the Ansible-deployed configurations

The migration scope is relatively small, as most of the content is already in Ansible format. The primary migration effort will involve:
- Converting the Chef server deployment scripts to Ansible playbooks
- Ensuring the existing Ansible playbooks follow best practices
- Maintaining the InSpec tests for compliance verification

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of Chef-specific components.

## Module Migration Plan

This repository contains a mix of Chef server setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only

### Target Details

Based on the source repository:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible playbook for configuration management platform deployment
- **Chef Server CLI**: Replace with Ansible playbook for configuration management server deployment
- **Test Kitchen with Ansible**: Maintain but update configuration to use pure Ansible testing approach

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be maintained in the migrated solution.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys are generated dynamically but should be managed securely

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible will require understanding of Chef server architecture and deployment requirements.
  - Mitigation: Create an Ansible role that handles Chef server deployment with similar configuration options.

- **InSpec Integration**: Maintaining the InSpec tests while moving to a pure Ansible workflow.
  - Mitigation: Use Ansible's built-in testing frameworks or continue to use InSpec as an external testing tool.

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible format)
   - Review and refactor according to Ansible best practices
   - Move variables to separate vars files
   - Consider converting to a reusable role

2. **poodle-vulnerability-fix** (low risk, already in Ansible format)
   - Review and refactor according to Ansible best practices
   - Consider merging with the website-https-configuration as an optional security enhancement

3. **chef-automate-deployment** (moderate complexity)
   - Create Ansible playbooks to replace the bash scripts
   - Use Ansible Vault for credential management
   - Create roles for Chef server and Automate deployment if needed

### Assumptions

1. The repository is primarily for demonstration purposes and not a production deployment.
2. The InSpec tests are intended to be maintained as part of the compliance automation strategy.
3. The Chef server deployment scripts are the primary components that need migration to Ansible.
4. The existing Ansible playbooks may need refactoring to follow best practices but are already in the target format.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing.
6. There are no external dependencies or integrations beyond what is visible in the repository.
7. The hardcoded credentials in the setup scripts are for demonstration purposes only.