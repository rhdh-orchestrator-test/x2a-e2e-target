# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations with a focus on demonstrating Chef InSpec for compliance testing alongside Ansible playbooks. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring a secure HTTPS website
2. Chef InSpec test profiles for validating security compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main focus will be on preserving the compliance testing functionality while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache with HTTPS, self-signed certificates, and a basic website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL module configuration, security hardening

- **ssh-compliance**:
    - Description: Chef InSpec profile that validates SSH server configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance checks

- **https-verification**:
    - Description: Chef InSpec profile that validates HTTPS website configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, SSL/TLS protocol validation, content verification

- **chef-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `index.html`: Sample HTML file for the website deployment

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - ansible-test for collection testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
- **SSH Hardening**: Ensure SSH security controls are maintained during migration
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates generated in the Ansible playbook
  - Consider migrating to Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification tasks or maintaining InSpec as a separate tool
  - Mitigation: Use ansible.builtin.assert or community.general.assert_cmd modules to perform similar validations
  
- **Chef Server Deployment**: Replacing Chef server deployment scripts with equivalent Ansible roles
  - Mitigation: Create an Ansible role for deploying alternative configuration management or compliance tools

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert inline templates to separate template files
   - Implement Ansible best practices (roles, variables)

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate with the website-https playbook as a role or included task
   - Implement idempotent checks

3. **InSpec tests** (moderate complexity)
   - Option 1: Create equivalent Ansible assertion tasks
   - Option 2: Create a role to install and run InSpec from Ansible

4. **Chef deployment scripts** (high complexity)
   - Determine if Chef server is still needed or can be replaced
   - Create Ansible roles for the chosen deployment approach

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. The self-signed certificates are for demonstration purposes and may need to be replaced with proper certificate management in production
4. The hardcoded credentials in the Chef deployment scripts are for demonstration only and would be replaced with secure credential management
5. The Test Kitchen configuration is primarily for testing and may not reflect the actual production deployment method
6. The SSH compliance tests suggest this is intended for a security-focused environment where STIG compliance may be required