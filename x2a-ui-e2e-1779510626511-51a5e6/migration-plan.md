# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks given the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a test page for the web server. No migration needed as it's a static content file.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Migrate to Ansible's built-in `assert` module for basic tests
  - Option 2: Use Molecule with Testinfra for more comprehensive testing
  - Option 3: Use Ansible's `command`/`shell` modules with `register` and assertions for direct command execution tests

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with different drivers and verifiers

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and only enables TLSv1.2
  - Approach: Convert the existing Ansible playbook (poodle_fix.yml) to an Ansible role with proper documentation

- **SSH Security**: The SSH security checks must be maintained
  - Approach: Convert the InSpec SSH profile to Ansible assertions or Molecule/Testinfra tests

- **Self-signed Certificates**: The process for generating self-signed certificates should be maintained
  - Approach: Keep using Ansible's `openssl_*` modules as they are already Ansible-native

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Recommendation: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Testinfra with Molecule which provides a Python-based testing framework with similar capabilities to InSpec

- **Compliance Metadata**: InSpec tests contain compliance metadata (STIG IDs, CCI numbers) that needs to be preserved
  - Mitigation: Add compliance metadata as comments or variables in Ansible roles and document the mapping

- **Chef Server/Automate Deployment**: The Chef server deployment scripts need to be replaced with Ansible equivalents
  - Mitigation: Create Ansible roles for deploying alternative compliance and configuration management tools

### Migration Order

1. **website_https_verify** (low risk, high value): Convert InSpec tests to Ansible/Molecule tests while maintaining existing Ansible playbook
2. **ssh_profile** (moderate complexity): Convert InSpec SSH compliance tests to Ansible/Molecule tests
3. **Chef Server/Automate Deployment Scripts** (high complexity): Replace with Ansible roles for alternative tools

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. The security compliance requirements (STIG, CCI) must be maintained in the new implementation
4. The deployment scripts for Chef Server and Automate are not critical to the main functionality and can be replaced with equivalent tools
5. No external Chef cookbooks or complex Chef-specific features are in use that would require special migration handling
6. The test environment setup (Test Kitchen) can be replaced with Molecule without significant impact
7. The self-signed certificate generation process can remain unchanged as it already uses Ansible modules