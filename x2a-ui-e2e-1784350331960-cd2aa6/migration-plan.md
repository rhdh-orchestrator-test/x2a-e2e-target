# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope involves converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving existing Ansible playbooks, and converting Chef deployment scripts to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers with HTTPS
    - Path: chef-and-ansible
    - Technology: Chef InSpec (for testing) and Ansible (for configuration)
    - Key Features: HTTPS website deployment with Apache, SSL/TLS compliance testing, SSH security testing, self-signed certificate generation

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server infrastructure
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation, system configuration

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website with Apache. Migration considerations: Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache. Migration considerations: Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality and TLS configuration. Migration considerations: Convert to Ansible-compatible testing framework like Molecule with Testinfra or Goss.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration considerations: Convert to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration considerations: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Convert to Ansible playbook or remove if not needed.

### Target Details

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment (based on hostname configuration in setup scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Ansible Molecule with Testinfra for Python-based testing
  - Option 2: Ansible Molecule with Goss for YAML-based testing
  - Option 3: Use the ansible-lint tool for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline integration
  - Compliance scanning can be handled by OpenSCAP integrated with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the TLS 1.2 requirement and disabled SSL3 as shown in the InSpec tests
  - Migration approach: Ensure Ansible playbooks maintain the same SSL/TLS configurations
  - Specific file: poodle_fix.yml contains critical security configuration for Apache

- **SSH Security**: The SSH root login restriction must be maintained
  - Migration approach: Convert the InSpec SSH profile to equivalent Ansible checks or OpenSCAP policies
  - Specific file: ssh_profile.rb contains CCI-000774 compliance check

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates in the website_https.yml playbook should use Ansible Vault for key storage
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Molecule with Testinfra which provides similar functionality to InSpec
  - Ensure test coverage remains the same by mapping InSpec resources to equivalent Testinfra modules

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Mitigation: Implement OpenSCAP with Ansible for compliance scanning and reporting
  - Consider AWX/Tower for dashboard and reporting capabilities

### Migration Order

1. **Ansible Playbooks** (low risk, high value)
   - Preserve existing website_https.yml and poodle_fix.yml playbooks
   - Update any deprecated Ansible syntax if needed

2. **Testing Framework** (moderate complexity)
   - Set up Molecule testing framework
   - Convert InSpec tests to Testinfra or Goss tests
   - Ensure test coverage remains the same

3. **Chef Automate/Infra Server Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement Ansible Vault for credential management
   - Set up AWX/Tower as a replacement for Chef Automate if needed

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes rather than production use, based on the README.md description.
2. The Chef InSpec tests are used for compliance verification of Ansible-managed systems, not for managing Chef-specific resources.
3. The setup-automate scripts are used for setting up a test environment and may not be needed in the final Ansible migration if an alternative compliance solution is chosen.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with proper secret management in production.
5. The self-signed certificates in the website_https.yml playbook are for testing purposes and would be replaced with proper certificates in production.
6. The migration will maintain the same level of security compliance as demonstrated in the InSpec tests.