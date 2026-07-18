# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation, along with bash scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks, and converting the Chef deployment scripts to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low to medium complexity.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of a web server
    - Path: chef-and-ansible
    - Technology: Chef InSpec (for testing) and Ansible (for configuration)
    - Key Features: HTTPS website deployment, SSL/TLS configuration testing, SSH security testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Migration consideration: Keep as-is or refactor to use Ansible collections.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Keep as-is or refactor to use Ansible collections.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website. Migration consideration: Convert to Ansible Molecule tests or another Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Convert to Ansible Molecule tests or another Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook or remove if not needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: ansible-test for module testing
  - Option 3: Maintain InSpec as a separate tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Vagrant can still be used as a driver for local testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for pipeline integration

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration approach: Maintain these security settings in the Ansible playbooks.
  
- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration approach: Convert to Ansible-compatible tests and ensure SSH hardening is maintained.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password): Replace with Ansible Vault for secure credential storage
  - Self-signed certificates: Maintain the same approach or consider integrating with Let's Encrypt for production environments

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing methodologies. Mitigation: Start with simple tests and gradually convert more complex ones.

- **Maintaining Compliance Validation**: Ensuring that compliance checks are properly translated from InSpec to Ansible testing frameworks. Mitigation: Create a validation matrix to ensure all compliance checks are preserved.

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible may not be necessary if the goal is to move away from Chef. Mitigation: Determine if Chef server deployment is still needed or if it can be eliminated.

### Migration Order

1. **Ansible Playbooks** (low risk, high value): Review and optimize existing Ansible playbooks (website_https.yml, poodle_fix.yml)
2. **Testing Framework** (moderate complexity): Convert InSpec tests to Ansible Molecule or other Ansible-compatible testing framework
3. **Chef Server Deployment** (high complexity): Convert Chef server deployment scripts to Ansible playbooks or eliminate if not needed

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies where possible.
2. The existing Ansible playbooks are functioning correctly and don't need significant changes.
3. The InSpec tests are currently used for compliance validation and this functionality needs to be preserved.
4. The Chef Automate and Chef Infra Server deployment scripts may be needed for legacy systems or could be eliminated.
5. No custom Chef cookbooks or recipes are present that would require complex migration.
6. The target environment will continue to be Ubuntu 20.04 or compatible systems.
7. Vagrant will continue to be used for local development and testing.
8. The security requirements (TLS 1.2, SSH hardening) need to be maintained in the migrated solution.