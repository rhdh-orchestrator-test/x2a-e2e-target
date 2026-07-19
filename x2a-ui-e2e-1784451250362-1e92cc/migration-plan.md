# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a complete migration. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing with InSpec

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef server deployment, user/organization creation, system configuration

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS support, creates self-signed certificates, and deploys a simple website. Migration considerations include preserving the SSL configuration and certificate generation.

- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2. Migration considerations include ensuring this security hardening is maintained.

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with equivalent Ansible testing framework.

- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS functionality and security. Migration considerations include converting to Ansible-native testing or maintaining InSpec as a testing tool.

- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible-native testing or maintaining InSpec as a testing tool.

- `setup-automate/deploy-automate.sh`: Shell script to deploy Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure deployment.

- `setup-automate/deploy-chef-server.sh`: Shell script to deploy Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like:
  - Ansible Lint for static code analysis
  - Molecule for Ansible role testing
  - Consider maintaining InSpec as a compliance tool if preferred, as it can work independently of Chef

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for centralized automation
  - GitLab/GitHub for version control and CI/CD

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the POODLE fix playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older, insecure protocols

- **Certificate Management**: The current solution generates self-signed certificates:
  - Consider integrating with Let's Encrypt for production environments
  - Maintain proper certificate storage and permissions (mode 0640)

- **SSH Security**: Maintain the SSH hardening rules defined in the InSpec profile:
  - Disable root login
  - Implement the CCI-000774 compliance controls
  - Maintain STIG compliance requirements (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy scripts (username/password combinations)

### Technical Challenges

- **Compliance Testing**: The repository demonstrates Chef InSpec for compliance testing with Ansible:
  - Decision needed: Keep InSpec for compliance or migrate to Ansible-native testing
  - If keeping InSpec, ensure proper integration with Ansible workflows
  - If migrating, ensure equivalent coverage of compliance checks, especially for the SSH security profile

- **Infrastructure Deployment**: The shell scripts for Chef server deployment need to be converted to Ansible playbooks:
  - Identify all system configurations (hostname, sysctl settings)
  - Create equivalent user and organization management in Ansible
  - Ensure proper handling of PEM files and certificates

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format):
   - `website_https.yml` - Minimal changes needed, focus on standardizing variable naming and module usage
   - `poodle_fix.yml` - Minimal changes needed, ensure handler naming consistency

2. **Testing Framework** (Medium complexity):
   - Convert Test Kitchen configuration to Molecule
   - Decision on InSpec: keep or replace with Ansible-native testing
   - Ensure all compliance checks are maintained regardless of testing framework

3. **Infrastructure Deployment** (Higher complexity):
   - Convert Chef server deployment scripts to Ansible playbooks
   - Implement secrets management with Ansible Vault
   - Create roles for system configuration and Chef server deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec for compliance testing alongside Ansible, not for production deployment.

2. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to cloud environments.

3. There is no complex data or state management that would complicate the migration.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secrets management in production.

5. The compliance requirements represented by the InSpec profiles are important to maintain in the migrated solution.

6. The self-signed certificates are for demonstration purposes and would be replaced with proper certificate management in production.

7. The Apache version (2.4.41-4ubuntu3.10) specified in the playbook is important and should be maintained in the migration.