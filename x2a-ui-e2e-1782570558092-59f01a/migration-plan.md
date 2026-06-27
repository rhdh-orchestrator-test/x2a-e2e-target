# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests for compliance verification
2. Chef Automate/Chef Server deployment scripts

The migration complexity is **LOW to MEDIUM** as most of the repository already contains Ansible playbooks. The primary focus will be on replacing Chef InSpec tests with Ansible-compatible testing frameworks and converting Chef server deployment scripts to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, depending on familiarity with Ansible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for verifying HTTPS website configuration, including port listening status, HTTP response, and SSL/TLS protocol security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response testing, SSL/TLS protocol security checks

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration, focusing on root login restrictions
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks, CCI compliance mapping

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `website_https.yml`: Ansible playbook for configuring HTTPS website with Apache. Already in Ansible format, no migration needed.
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Already in Ansible format, no migration needed.
- `index.html`: Simple HTML file used for testing. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - **Option 1**: Migrate to Ansible Molecule with testinfra for testing
  - **Option 2**: Use Ansible's assert module for basic compliance testing
  - **Option 3**: Implement custom Python scripts using pytest for more complex testing scenarios

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles for:
  - Installing and configuring equivalent functionality using:
    - AWX/Ansible Tower for web UI and job scheduling (replacing Chef Automate)
    - Ansible Collections for configuration management (replacing Chef Server)
    - Ansible Semaphore as a lightweight alternative

### Security Considerations

- **SSH Security Profile**: Ensure migration preserves security compliance checks:
  - Migrate the SSH root login check to Ansible assert tasks
  - Maintain compliance metadata (CCI IDs, STIG IDs) in Ansible task documentation

- **SSL/TLS Security**: Ensure migration preserves security hardening:
  - Maintain TLS 1.2 requirement and disable insecure protocols
  - Preserve certificate generation and management

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - SSL/TLS certificate references should use Ansible's certificate management modules

### Technical Challenges

- **Compliance Testing Framework**: InSpec provides rich testing capabilities specifically designed for compliance testing. Finding an equivalent in the Ansible ecosystem may require combining multiple tools:
  - Mitigation: Use Ansible Molecule with testinfra for infrastructure testing, and implement custom modules for specific compliance checks

- **Compliance Metadata**: InSpec tests include rich compliance metadata (CCI IDs, STIG references) that needs to be preserved:
  - Mitigation: Store compliance metadata in Ansible task documentation or in separate YAML files that can be referenced

- **Chef Server Functionality**: The deployment scripts set up Chef Server with specific organizations and users:
  - Mitigation: Design Ansible roles that configure AWX/Tower with equivalent organizations and users

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Already in Ansible format, no migration needed
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible Molecule/testinfra tests
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles for deploying equivalent infrastructure

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The hardcoded credentials in the deployment scripts are examples and not used in production environments.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the scripts mention they can work on cloud VMs as well.
4. The repository is primarily educational/demonstrational in nature, showing integration between Chef InSpec and Ansible rather than being a full production system.
5. There are no external dependencies or integrations beyond what's explicitly shown in the files.
6. The migration will focus on replacing Chef InSpec with Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.
7. The Chef Automate and Chef Server deployment scripts are intended for demonstration purposes and not part of a larger Chef infrastructure.