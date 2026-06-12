# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. A Chef InSpec testing framework used alongside Ansible playbooks
2. Chef Automate and Chef Infra Server deployment scripts
3. Ansible playbooks for configuring web servers with HTTPS

The migration complexity is **LOW to MEDIUM** as most of the Ansible components can be directly reused, while the Chef InSpec tests need to be converted to Ansible-native testing solutions. The Chef server deployment scripts need to be replaced with Ansible playbooks for infrastructure management.

**Estimated Timeline**: 2-3 weeks for a complete migration, with the following breakdown:
- 1 week: Convert InSpec tests to Ansible testing framework
- 1 week: Replace Chef server deployment scripts with Ansible equivalents
- 3-5 days: Testing and validation

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers
    - Path: chef-and-ansible/
    - Technology: Hybrid (Ansible playbooks with Chef InSpec tests)
    - Key Features: HTTPS configuration, SSL/TLS security testing, compliance verification

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef infrastructure
    - Key Features: Chef server deployment, user and organization creation, configuration management

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be directly reused in the Ansible migration.
- `poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly reused in the Ansible migration.
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Needs conversion to Ansible testing framework.
- `tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible testing framework.
- `deploy-automate.sh`: Bash script for deploying Chef Automate. Needs replacement with Ansible playbook.
- `deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs replacement with Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-test for unit and integration testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing and development

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for configuration management
  - CI/CD pipelines for automated testing and deployment

### Security Considerations

- **SSL/TLS Configuration**: The current implementation configures Apache with TLS 1.2 and disables older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the same SSL/TLS configurations in the Ansible playbooks

- **SSH Security**: The repository includes SSH security compliance tests.
  - Migration approach: Convert InSpec SSH tests to Ansible assert statements or Molecule verifiers

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-native testing requires careful mapping of test assertions.
  - Mitigation: Create a mapping document for InSpec to Ansible test conversions and validate each test case individually.

- **Infrastructure Management**: Replacing Chef Automate/Infra Server with Ansible-native solutions requires rethinking the infrastructure management approach.
  - Mitigation: Design an Ansible AWX/Tower deployment playbook with equivalent user/organization management.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, can be directly reused
2. **InSpec Tests** - Convert to Ansible testing framework
3. **Chef Server Deployment Scripts** - Replace with Ansible playbooks for infrastructure management

### Assumptions

1. The current setup uses Chef InSpec primarily for testing, not for configuration management.
2. The target environment will continue to be Ubuntu 20.04 or compatible systems.
3. Vagrant will continue to be used for development/testing environments.
4. The organization does not require Chef-specific features that might not have direct Ansible equivalents.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and not production values.
6. The self-signed certificates in the web server configuration are acceptable for the target environment or will be replaced with proper certificates.