# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, Test Kitchen integration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec tests. Migration will require converting to Ansible Molecule or another Ansible-native testing framework.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for compliance testing
  - Option 3: OpenSCAP with Ansible integration for compliance testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and control
  - Ansible Content Collections for configuration management
  - Compliance scanning tools like OpenSCAP or Ansible Compliance Automation

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL/TLS hardening (disabling SSLv3, enabling TLSv1.2). Ensure these security controls are maintained in the Ansible migration.
  - Migration approach: Preserve the existing Ansible tasks in poodle_fix.yml that handle SSL configuration.

- **SSH Security**: The repository includes SSH hardening tests (disabling root login). Ensure these security controls are maintained in the Ansible migration.
  - Migration approach: Convert the InSpec SSH tests to equivalent Ansible checks or use Ansible-compatible compliance tools.

- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider implementing proper certificate management in the Ansible migration.
  - Migration approach: Use Ansible's certificate management modules or integrate with external certificate authorities.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of InSpec resources to equivalent testing constructs.
  - Mitigation: Create a mapping document for InSpec to Ansible testing constructs and validate each test conversion individually.

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem for Chef Automate features.
  - Mitigation: Evaluate Ansible AWX/Tower features against Chef Automate requirements and identify any gaps that need custom solutions.

- **Testing Integration**: Ensuring the new Ansible testing framework integrates smoothly with CI/CD pipelines.
  - Mitigation: Set up proof-of-concept CI/CD pipelines early in the migration process to validate the testing approach.

### Migration Order

1. **Ansible Playbooks** (Low risk, high value)
   - Preserve existing website_https.yml and poodle_fix.yml playbooks
   - Update any deprecated syntax or modules

2. **InSpec Tests** (Moderate complexity)
   - Convert website_https_verify.rb to Ansible-compatible tests
   - Convert ssh_profile.rb to Ansible-compatible tests

3. **Chef Deployment Scripts** (High complexity)
   - Create Ansible playbooks to replace deploy-automate.sh
   - Create Ansible playbooks to replace deploy-chef-server.sh

4. **Test Kitchen Configuration** (Moderate complexity)
   - Replace kitchen.yml with Ansible Molecule configuration

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec integration with Ansible, not to provide production-ready infrastructure code.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The deployment scripts for Chef Automate and Chef Infra Server are used for demonstration purposes and not for critical production environments.
5. There are no external dependencies or integrations not visible in the repository files.
6. The migration will focus on functional equivalence rather than exact replication of the Chef InSpec testing approach.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure credential management in the migration.