# MIGRATION FROM CHEF AND BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests that are used alongside Ansible for compliance automation
2. Bash scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** as the repository already contains Ansible playbooks, and the main task will be converting the Bash deployment scripts to Ansible playbooks. Estimated timeline: **1-2 weeks** for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: A set of Ansible playbooks with Chef InSpec tests for compliance automation
    - Path: chef-and-ansible/
    - Technology: Ansible + Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing with InSpec

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should include converting to Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website. Already in Ansible format, but should be reviewed for best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Already in Ansible format, but should be reviewed for best practices.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible's built-in assert module for basic tests, or integrate with Ansible using the `inspec` module for more complex compliance testing
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible playbooks
- **Chef Automate CLI**: Create Ansible roles to handle the installation and configuration of Chef Automate and Chef Infra Server

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in the Ansible migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already demonstrated in the existing playbooks.

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Create Ansible tasks to configure SSH properly and use Ansible's assert module to verify compliance.

- **Vault/secrets management**:
  - Hardcoded credentials in Bash scripts (username, password) should be moved to Ansible Vault.
  - Count: 2 credential sets in setup-automate scripts (username/password combinations)

### Technical Challenges

- **Chef InSpec Tests**: The repository uses Chef InSpec for compliance testing. 
  - Mitigation: Either continue using InSpec with Ansible (as shown in the examples) or migrate tests to Ansible's native testing capabilities.

- **Chef Automate and Chef Infra Server Deployment**: The Bash scripts deploy Chef infrastructure.
  - Mitigation: Create Ansible roles for deploying Chef components or consider migrating completely away from Chef to Ansible-native solutions.

### Migration Order

1. **chef-and-ansible playbooks** (low risk, already in Ansible format)
   - Review and refactor existing Ansible playbooks for best practices
   - Convert InSpec tests to Ansible assertions where possible

2. **setup-automate scripts** (moderate complexity)
   - Convert Bash scripts to Ansible playbooks
   - Implement Ansible Vault for credential management
   - Create roles for Chef Automate and Chef Infra Server deployment

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the main README.md mentioning "working examples" related to content created by Technical Product Marketing.

2. The Chef InSpec tests are intended to work alongside Ansible for compliance automation, not as part of a larger Chef-based infrastructure.

3. The setup-automate scripts are standalone deployment scripts and not part of a larger automation framework.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the scripts are designed to work on both on-premises and cloud VMs.

5. There is no complex data structure or state management that would require special handling during migration.

6. The hardcoded credentials in the Bash scripts are for demonstration purposes and would be replaced with proper secret management in a production environment.