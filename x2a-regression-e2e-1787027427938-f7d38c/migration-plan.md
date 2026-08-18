# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them to follow best practices
3. Maintaining Chef InSpec tests for compliance validation while integrating them into an Ansible-native workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings
- `chef-and-ansible/index.html`: Simple HTML file for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on any cloud or on-premises VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing but integrate with Ansible using the `community.general.inspec` module or Ansible's built-in `assert` module
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that achieve the same configuration

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migrated Ansible roles.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. Ensure this security check is maintained and implemented in the Ansible configuration.
- **Vault/secrets management**: 
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password) should be moved to Ansible Vault
  - No other credentials detected in the codebase

### Technical Challenges

- **Chef InSpec Integration**: Determining the best approach to integrate InSpec tests with Ansible (options include using the `community.general.inspec` module, converting tests to Ansible assertions, or maintaining InSpec as a separate tool in the CI/CD pipeline)
- **Chef Automate Configuration**: Ensuring all Chef Automate and Chef Server configuration options are properly translated to Ansible equivalents
- **Testing Framework**: Replacing Test Kitchen with Molecule while maintaining the same level of test coverage

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already in Ansible format; focus on standardizing to follow best practices and role-based structure
2. **Chef Deployment Scripts** (setup-automate/*.sh): Convert to Ansible playbooks, focusing on idempotence and security
3. **Testing Framework**: Set up Molecule testing to replace Test Kitchen while preserving InSpec tests

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README description
2. The Chef InSpec tests are valuable and should be preserved rather than rewritten
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
5. The Apache configuration is intended to be a simple example and may need enhancement for production use
6. The repository doesn't contain actual Chef cookbooks or recipes that need migration, only deployment scripts for Chef infrastructure
7. The existing Ansible playbooks are functional but may benefit from restructuring into roles for better maintainability