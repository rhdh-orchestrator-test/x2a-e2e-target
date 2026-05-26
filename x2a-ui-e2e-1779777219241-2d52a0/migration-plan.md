# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Based on the repository analysis, this is a low-complexity migration that should take approximately 1-2 weeks to complete, with the primary focus on converting InSpec tests to Ansible testing frameworks like Molecule or ansible-test.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec test profile that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML content for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule for test-driven infrastructure development
  - Option 2: Use ansible-lint for static analysis of playbooks
  - Option 3: Use pytest-ansible for Python-based testing of infrastructure

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the ansible_playbook provisioner but replace InSpec verifier

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for configuration management platform deployment
  - Consider migrating to AWX/Ansible Tower as the centralized management platform

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible playbook to an Ansible role with proper documentation
  - Ensure the SSL protocol restrictions are maintained (TLSv1.2 only)

- **SSH Security**: The SSH security controls tested by the InSpec profile need to be implemented and tested in Ansible
  - Approach: Create an Ansible role for SSH hardening that implements the same controls
  - Add Ansible-native tests to verify SSH configuration meets security requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's testing frameworks
  - Mitigation: Create a mapping of InSpec resources to Ansible modules/assertions
  - Example: InSpec's `describe port(443)` can be replaced with Ansible's `wait_for` module or Molecule's testinfra

- **Compliance Metadata**: InSpec tests contain rich compliance metadata (STIG IDs, CCI references)
  - Mitigation: Preserve compliance metadata in Ansible role documentation
  - Consider implementing custom Ansible callback plugins to generate compliance reports

- **Test Kitchen Integration**: Current workflow uses Test Kitchen for orchestration
  - Mitigation: Either maintain Test Kitchen with ansible_playbook provisioner or migrate to Molecule

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Convert to Ansible roles with proper structure (low risk, already in Ansible)
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing (moderate complexity)
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks (moderate complexity)
4. **Test Kitchen Configuration**: Replace with Molecule or update for pure Ansible workflow (low risk)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 systems
3. The security requirements (TLS 1.2, SSH hardening) must be maintained in the migrated solution
4. The Chef Automate/Infra Server deployment scripts are used for demonstration and not critical production infrastructure
5. No external Chef cookbooks or complex Chef-specific features are being used that would require special migration handling