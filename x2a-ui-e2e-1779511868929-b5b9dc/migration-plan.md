# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a pure Chef cookbook repository. The migration scope is relatively small, as most of the infrastructure code is already in Ansible format, with Chef components primarily used for testing and compliance validation.

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the limited Chef-specific components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Sample HTML file used for testing web server deployment. No migration needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in setup-automate script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider maintaining InSpec as a standalone testing tool that can be called from Ansible

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Ensure the same SSL protocol restrictions are implemented in the migrated Ansible roles
  
- **SSH Security**: The SSH security checks in ssh_profile.rb need to be preserved
  - Approach: Convert InSpec tests to Ansible assert statements or maintain as separate InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Consider using Ansible's assert module or maintaining InSpec as a separate testing tool called from Ansible
  
- **Test Kitchen Integration**: Replacing Test Kitchen with Molecule
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen setup

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format; focus on refactoring to follow best practices
2. **Chef Automate Deployment Scripts**: Convert bash scripts to Ansible roles for Chef server deployment
3. **InSpec Tests**: Convert to Ansible assertions or maintain as separate InSpec tests called from Ansible

### Assumptions

1. The primary goal is to migrate all components to pure Ansible, including replacing InSpec tests with Ansible-native testing
2. The current setup is used primarily for demonstration/educational purposes rather than production
3. The Chef Automate and Chef Server deployment scripts are intended to be migrated to Ansible rather than maintained as-is
4. No external Chef cookbooks or complex Chef-specific features are in use beyond what's visible in the repository
5. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credential management in the migrated solution