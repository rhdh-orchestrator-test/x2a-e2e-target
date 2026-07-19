# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec testing integration

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a complete migration. The primary focus will be on:
- Converting Chef deployment scripts to Ansible roles
- Preserving the InSpec testing functionality within an Ansible framework
- Ensuring security configurations are properly maintained

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: SSL/TLS configuration, Apache web server setup, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should include converting to Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be directly used in the Ansible migration with minimal changes.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be directly used in the Ansible migration with minimal changes.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be preserved and integrated with Ansible testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be preserved and integrated with Ansible testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to Ansible roles.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to Ansible roles.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible integration for InSpec or migrate to native Ansible testing tools:
  - Option 1: Continue using InSpec with Ansible by installing InSpec and running tests via Ansible
  - Option 2: Convert InSpec tests to Ansible assert modules or molecule verifiers

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management solution:
  - Convert deployment scripts to Ansible roles for infrastructure setup
  - Consider migrating to AWX/Tower for web UI and role-based access control

- **Test Kitchen with Ansible**: Replace with Ansible Molecule for testing:
  - Convert kitchen.yml configuration to molecule.yml
  - Integrate existing InSpec tests with Molecule verifiers

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain secure TLS configurations:
  - Preserve the TLS 1.2 requirement and disabled SSL3 (from poodle_fix.yml)
  - Ensure proper certificate generation and management (from website_https.yml)

- **SSH Security**: Maintain SSH hardening configurations:
  - Preserve the SSH root login restriction (from ssh_profile.rb)
  - Ensure proper SSH restart handlers are maintained

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using Ansible Vault or external certificate management
  - Count of credentials detected: 3 (username, password, email in deployment scripts)

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with Ansible:
  - Challenge: InSpec tests are currently integrated with Test Kitchen
  - Mitigation: Use Ansible's command module to run InSpec tests or migrate to Molecule with InSpec verifier

- **Chef Server Deployment**: Converting Chef server deployment to Ansible:
  - Challenge: The deployment scripts install Chef-specific components
  - Mitigation: Create Ansible roles that either install Chef components or replace them with Ansible equivalents (AWX/Tower)

### Migration Order

1. **chef-and-ansible Ansible Playbooks** (low risk, high value):
   - Already in Ansible format, minimal changes needed
   - Convert Test Kitchen to Molecule for testing
   - Preserve InSpec tests

2. **setup-automate Deployment Scripts** (moderate complexity):
   - Convert Bash scripts to Ansible roles
   - Implement Ansible Vault for credentials
   - Create idempotent deployment process

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool, while preserving the compliance testing capabilities of InSpec.
2. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced with equivalent Ansible functionality, not necessarily to deploy Chef components.
3. The security configurations and compliance tests are critical and must be maintained in the migration.
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs, with potential deployment to cloud environments.
5. There is no requirement to maintain backward compatibility with Chef-specific components.
6. The InSpec tests should be preserved and integrated with Ansible testing frameworks.
7. The hardcoded credentials in the deployment scripts will be replaced with secure credential management in Ansible.