# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and server deployment. The migration scope is relatively small, primarily involving Chef InSpec tests that are already designed to work with Ansible playbooks, and Chef server/Automate deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and the existing Ansible integration.

## Module Migration Plan

This repository contains Chef InSpec tests and deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **Chef InSpec Tests**:
    - Description: Compliance tests for verifying HTTPS website configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response validation, SSL protocol verification, SSH configuration validation

- **Chef Server/Automate Deployment**:
    - Description: Bash scripts for deploying Chef Infra Server and Chef Automate
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: User creation, organization setup, system configuration

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS website. Migration consideration: Already in Ansible format, can be used as-is.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Already in Ansible format, can be used as-is.
- `chef-and-ansible/index.html`: Sample HTML file for testing. Migration consideration: Can be used as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a testing tool but invoke it directly from Ansible

- **Chef Server/Automate**: Replace deployment scripts with Ansible playbooks that:
  - Configure system parameters (hostname, sysctl settings)
  - Install and configure alternative configuration management or compliance tools

### Security Considerations

- **SSL Configuration**: The repository includes specific SSL hardening (disabling SSLv3, enabling TLSv1.2). Ensure these security configurations are maintained in the Ansible migration.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Ensure Ansible playbooks implement the same security controls.
- **Credentials in Scripts**: The deployment scripts contain hardcoded credentials. Migrate to Ansible Vault for secure credential storage.

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or another testing framework may require careful mapping of test logic.
  - Mitigation: Consider keeping InSpec as a testing tool and invoking it from Ansible if direct conversion is challenging.

- **Chef Server Replacement**: Determining what to replace Chef Server/Automate with depends on organizational needs.
  - Mitigation: Evaluate if AWX/Tower, Ansible Semaphore, or other Ansible management platforms meet the requirements.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Already in Ansible format, no migration needed
2. **Chef Server/Automate Deployment Scripts**: Convert to Ansible playbooks
3. **InSpec Tests**: Convert to Ansible-compatible testing framework or integrate InSpec with Ansible

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README mentioning "working examples" and "companion to a white paper".
2. The InSpec tests are intended to verify the configurations applied by the Ansible playbooks, showing how Chef InSpec can be used alongside Ansible.
3. The deployment scripts are used to set up Chef Server and Automate for demonstration or testing purposes.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no additional Chef cookbooks or resources beyond what is visible in the repository.
6. The migration goal is to eliminate Chef components while maintaining the same functionality using Ansible.