# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be on using Chef InSpec for compliance testing alongside Ansible for configuration management. There are also Chef server and Chef Automate deployment scripts. The migration scope is relatively small, with only a few files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: A demonstration of using Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: InSpec tests for HTTPS website verification and SSH security compliance

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's built-in assert module for simple tests
  - Option 2: Use Ansible Lint for static analysis
  - Option 3: Integrate with Molecule for testing
  - Option 4: Keep InSpec as a separate tool and call it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in testing capabilities

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL configuration for Apache web server with specific security settings (disabling SSLv3, enabling TLSv1.2)
  - Migration approach: Maintain the same security settings in Ansible tasks

- **SSH Security**: InSpec tests for SSH root login security
  - Migration approach: Implement equivalent checks using Ansible's assert module or maintain InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible assertions or maintaining them as separate components
  - Mitigation: Consider keeping InSpec as a separate tool called from Ansible if direct conversion is challenging

- **Chef Automate/Server Deployment**: Replacing Chef server deployment scripts with Ansible equivalents
  - Mitigation: Create Ansible roles for deploying alternative compliance and configuration management tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes
2. **InSpec Tests**: Convert to Ansible assertions or integrate as external tests
3. **Chef Deployment Scripts**: Replace with Ansible roles for deploying alternative tools

### Assumptions

1. The primary purpose of this repository is to demonstrate the integration of Chef InSpec with Ansible for compliance automation, not to provide production-ready infrastructure code.
2. The Chef server deployment scripts are used for demonstration purposes and are not critical to the main functionality.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The security requirements (SSL/TLS configuration, SSH security) need to be maintained in the migrated solution.
5. There are no external dependencies or complex Chef cookbooks to migrate, as this repository focuses on InSpec tests and simple Ansible playbooks.
6. The migration will focus on maintaining the same functionality while moving away from Chef-specific components.
7. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure alternatives in the migrated solution.