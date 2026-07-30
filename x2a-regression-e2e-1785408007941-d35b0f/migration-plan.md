# MIGRATION FROM ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format while preserving the compliance testing capabilities provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a single developer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to reflect the new Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test that verifies HTTPS configuration on the web server. Can be preserved as-is for compliance testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test that verifies SSH root login is disabled. Can be preserved as-is for compliance testing.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment. Can be preserved as-is or moved to a templates directory.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen-ansible)**: Replace with Ansible Molecule for testing or update Test Kitchen configuration to work with the new Ansible structure
- **Chef InSpec**: Preserve InSpec for compliance testing, as it's a key feature of this repository
- **Apache2 (2.4.41-4ubuntu3.10)**: Continue using this specific version in the migrated Ansible playbooks

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLSv1.2 and disable SSLv3 to address the POODLE vulnerability. This security hardening should be preserved in the migration.
- **Self-signed Certificates**: The playbooks generate self-signed certificates for HTTPS. Consider enhancing this with Let's Encrypt integration for production use.
- **SSH Hardening**: The InSpec tests verify that SSH root login is disabled. This compliance check should be preserved.
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef Automate and Chef Server deployment scripts (username, password, email)
  - These should be moved to Ansible Vault or another secrets management solution

### Technical Challenges

- **Preserving InSpec Integration**: Ensuring that the InSpec tests continue to work with the migrated Ansible structure. This can be addressed by maintaining the same system state after playbook execution.
- **Chef Automate/Server Deployment**: Converting the bash scripts for Chef Automate and Chef Server deployment to Ansible roles. This will require careful handling of the installation process and configuration.

### Migration Order

1. **website_https.yml** (low risk, high value): Convert to an Ansible role with proper directory structure
2. **poodle_fix.yml** (low risk): Convert to an Ansible role or include as a task in the website_https role
3. **Chef deployment scripts** (moderate complexity): Convert to Ansible roles with proper variable handling and secrets management

### Assumptions

1. The primary goal is to maintain the same functionality while improving the Ansible code structure and practices.
2. Chef InSpec will continue to be used for compliance testing.
3. The target environment will remain Ubuntu 20.04 or compatible systems.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with proper secrets management.
5. The repository is primarily used for demonstration and educational purposes rather than production deployments.