# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

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
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration security check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server. Can be directly used in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible's built-in assert module or ansible-lint for basic tests, or integrate with other testing frameworks like Molecule, TestInfra, or maintain InSpec as a separate testing tool
- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Vagrant (latest)**: Can continue to be used with Molecule or other Ansible testing frameworks
- **Apache2 (2.4.41-4ubuntu3.10)**: Continue to manage with Ansible apache2 module
- **OpenSSL**: Continue to manage with Ansible openssl_* modules

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook that enforces TLSv1.2 and disables older protocols
- **Self-signed Certificates**: The certificate generation process should be preserved in the migration
- **SSH Security**: The SSH root login restriction testing should be maintained
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate paths and configurations should be properly secured
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of test assertions
  - Mitigation: Consider using TestInfra with Molecule which provides similar functionality to InSpec but is Python-based and integrates well with Ansible
  
- **Chef Automate/Server Deployment**: The Chef server deployment scripts need to be replaced with equivalent Ansible roles
  - Mitigation: Create Ansible roles that perform the same system configurations and potentially deploy alternative compliance and automation tools

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible-compatible testing)
4. **Chef Deployment Scripts** (high complexity, requires complete replacement)

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining or enhancing the compliance testing capabilities
2. The existing Ansible playbooks can be used with minimal modifications
3. There is no requirement to maintain backward compatibility with Chef Automate or Chef Infra Server
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The security requirements and compliance standards referenced in the InSpec tests (e.g., SRG-OS-000112) must be maintained in the Ansible solution
6. The self-signed certificate approach is acceptable for the migrated solution
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution