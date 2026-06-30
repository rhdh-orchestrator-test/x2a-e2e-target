# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating security compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** as most of the repository already contains Ansible playbooks. The primary focus will be on replacing Chef InSpec tests with Ansible-compatible testing frameworks and replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks.

**Estimated Timeline**: 2-3 weeks

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup, virtual hosts, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Self-signed certificate generation, virtual host configuration, SSL/TLS security settings

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **compliance-testing**:
    - Description: InSpec tests for validating HTTPS website configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content validation, SSL/TLS protocol verification, SSH root login security check

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing web server deployment. Migration consideration: Can be used as-is or templated in Ansible.
- `deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure deployment.
- `deploy-chef-server.sh`: Script to deploy Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible assert modules for inline testing
  - Option 3: Use community.general.assert module for more complex assertions

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Consider using Ansible Collections for role organization

### Security Considerations

- **SSL/TLS Configuration**: The current implementation disables SSLv3 and enables only TLSv1.2. Migration should maintain or improve this security posture by:
  - Ensuring modern TLS protocols (TLS 1.2/1.3) are enabled
  - Disabling weak ciphers
  - Implementing proper certificate management

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain SSH hardening checks
  - Implement equivalent controls in Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, email in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions and may require additional modules or custom scripts.
  - Mitigation: Use Ansible's assert module or Molecule with Testinfra to replicate InSpec functionality.

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible infrastructure.
  - Mitigation: Implement Ansible AWX/Tower deployment playbooks and document the transition process for users.

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Add documentation and improve variable usage

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate with main website configuration playbook
   - Enhance with additional security hardening

3. **compliance-testing** (medium complexity)
   - Convert InSpec tests to Ansible Molecule tests
   - Ensure all security checks are maintained

4. **chef-infrastructure-deployment** (high complexity)
   - Create Ansible playbooks to replace Chef deployment scripts
   - Document transition process for users

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README mentioning "examples" and "companion to a white paper".

2. The Chef InSpec tests are used for compliance validation of infrastructure deployed with Ansible, suggesting a hybrid approach that can be consolidated to pure Ansible.

3. The deployment scripts contain default/example credentials that would be replaced in production environments.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, though the deployment scripts could be used on other Linux distributions.

5. There is no complex data persistence or state management that would complicate migration.

6. Users of this repository are familiar with both Chef and Ansible, making the transition more straightforward from a knowledge perspective.

7. The Apache configuration is relatively standard and doesn't contain highly customized or legacy configurations that would be difficult to migrate.