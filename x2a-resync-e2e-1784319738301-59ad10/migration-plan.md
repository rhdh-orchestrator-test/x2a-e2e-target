# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with InSpec testing
3. InSpec compliance profiles for security validation

The migration complexity is relatively low as most of the Ansible components are already in place. The primary focus will be on replacing the Chef server deployment scripts with Ansible equivalents and ensuring the InSpec testing framework continues to function within an Ansible-only workflow.

Estimated timeline: 1-2 weeks for a complete migration, with minimal disruption to existing operations.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website configuration, SSL/TLS security settings, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability by enforcing TLSv1.2. Migration considerations include ensuring this security fix is incorporated into the main playbook.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include updating to use Ansible-native testing frameworks or adapting to continue using InSpec.
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include preserving these tests for continuous compliance validation.
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include integrating this into the Ansible workflow.
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible playbooks for infrastructure deployment.
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible playbooks for infrastructure deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Retain as a compliance testing tool but integrate with Ansible workflow using the `ansible.builtin.shell` module or dedicated Ansible roles for InSpec execution
- **Test Kitchen**: Replace with Ansible Molecule for testing or adapt kitchen.yml to work with Ansible-only workflow
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible-native orchestration tools

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in poodle_fix.yml that enforces TLSv1.2
- **SSH Security**: The SSH compliance profile must be integrated into the Ansible workflow
- **Certificate Management**: Self-signed certificate generation should be preserved or enhanced with Let's Encrypt integration
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL/TLS certificate references should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL key)

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to run as part of the Ansible workflow may require additional configuration or custom modules
- **Chef Server Replacement**: Determining the appropriate Ansible-native replacement for Chef Server functionality (AWX/Tower or alternative)
- **Testing Framework**: Adapting or replacing Test Kitchen with Ansible-native testing tools while preserving test coverage

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Consolidate website_https.yml and poodle_fix.yml into a single playbook with proper role structure
2. **InSpec Tests** (Moderate complexity): Adapt InSpec tests to run within Ansible workflow
3. **Chef Server Deployment** (High complexity): Replace Chef server deployment scripts with Ansible playbooks for infrastructure management

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than production deployment
2. The Chef Automate and Chef Infra Server deployment is intended for on-premises or generic cloud VMs
3. There are no external dependencies or integrations not visible in the repository
4. The hardcoded credentials in the deployment scripts are examples and not used in production
5. The InSpec tests are intended to be run as part of a CI/CD pipeline or manual verification process
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. There are no database or application components beyond the web server configuration
8. The migration will preserve the compliance testing functionality while eliminating Chef server components