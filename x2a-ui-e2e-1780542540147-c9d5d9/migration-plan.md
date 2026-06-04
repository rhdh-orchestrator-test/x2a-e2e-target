# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with tools like Ansible Lint or OpenSCAP
  - Option 3: Keep InSpec but call it from Ansible using the command module

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Ansible AWX/Tower for web UI, job scheduling, and inventory management
  - Ansible Galaxy for role sharing
  - Git repositories for version control

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS protocols are enforced in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL configuration but update to current best practices.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create equivalent Ansible tasks to verify and enforce SSH security settings.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or checks.
  - Mitigation: Use Ansible's assert module or consider keeping InSpec as a separate testing tool called from Ansible.

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible automation platform.
  - Mitigation: Document clear steps for setting up Ansible AWX/Tower as a replacement for Chef Server/Automate.

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format, just need review and potential updates
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Moderate complexity to convert to Ansible testing framework
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - High complexity, requires architectural decisions about Ansible management platform

### Assumptions

1. The primary goal is to consolidate on Ansible as the sole configuration management and compliance tool.
2. The InSpec tests are currently being used for compliance verification after Ansible playbook execution.
3. There is no direct integration with external systems beyond what's visible in the repository.
4. The deployment scripts are used for setting up Chef infrastructure, which would be replaced by Ansible infrastructure.
5. No custom Chef resources or complex Chef-specific functionality is being used that would require special handling.
6. The target environment will continue to be Ubuntu 20.04 or compatible systems.
7. The self-signed certificates approach is acceptable for the migrated solution.