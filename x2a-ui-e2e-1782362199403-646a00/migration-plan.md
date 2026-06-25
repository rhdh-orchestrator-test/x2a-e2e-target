# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be primarily focused on examples rather than production infrastructure code. The migration scope is relatively small, consisting of:

1. Chef InSpec test profiles that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks

The migration complexity is low to medium, with an estimated timeline of 1-2 weeks for a single developer to complete the migration. The primary focus will be on preserving the compliance testing functionality while moving away from Chef-specific components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic tests
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Consider integrating with other compliance tools like OSCAP or Ansible's own compliance capabilities

- **Test Kitchen (latest)**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible automation controller (AWX/Tower) or other orchestration tools

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the Apache configuration
  - Migration approach: Ensure the Ansible playbooks maintain the same SSL protocol restrictions (TLSv1.2 only)

- **SSH Hardening**: The SSH security controls tested by InSpec need to be implemented in Ansible
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Create custom Ansible modules or use the `assert` module with appropriate conditions
  - Consider using Ansible's built-in `uri` module to replace the HTTP testing functionality

- **Chef Server Functionality**: Replacing Chef Server's functionality with Ansible equivalents
  - Mitigation: Identify which Chef Server features are actually needed and implement them using Ansible Tower/AWX or other tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, convert to Ansible assertions or Molecule tests
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, replace with Ansible playbooks for infrastructure setup

### Assumptions

1. The repository is primarily for demonstration purposes and not production infrastructure
2. The InSpec tests are the primary value to preserve in the migration
3. The deployment scripts are examples and not actively used in production
4. There is no dependency on Chef-specific features that would be difficult to replicate in Ansible
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The migration will not require preserving backward compatibility with Chef tools
7. The hardcoded credentials in the deployment scripts are for demonstration only and not actual production credentials