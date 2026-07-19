# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with two main components:

1. A set of Ansible playbooks with Chef InSpec tests for compliance verification
2. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for compliance verification of web servers
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL/TLS configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with Ansible-native testing framework or adapting to use Molecule.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible-native testing or maintaining InSpec integration.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible-native testing or maintaining InSpec integration.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for deployment of alternative compliance platforms.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for deployment of alternative configuration management platforms.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing frameworks like Molecule or maintain InSpec as a standalone compliance tool integrated with Ansible
- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing
- **Chef Automate**: Replace with alternative compliance platforms like Ansible Tower/AWX with compliance scanning capabilities
- **Chef Infra Server**: Replace with Ansible-based configuration management approach

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening for Apache SSL configuration (disabling SSLv3, enabling only TLSv1.2)
- **SSH Hardening**: The SSH compliance profile must be preserved in the Ansible-native solution
- **Certificate Management**: Self-signed certificate generation must be maintained in the Ansible playbooks
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely

### Technical Challenges

- **Compliance Testing Framework**: Deciding whether to maintain Chef InSpec for compliance testing or migrate to an Ansible-native solution. InSpec provides robust compliance testing capabilities that may not be fully replicated in Ansible-native tools.
  - Mitigation: Consider maintaining InSpec as a standalone tool called from Ansible or investigate Ansible Lint and custom modules for compliance testing.

- **Test Kitchen Integration**: The current setup uses Test Kitchen for testing Ansible playbooks with InSpec verification.
  - Mitigation: Replace with Molecule for Ansible role testing, which provides similar functionality in an Ansible-native way.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Migrate website_https.yml and poodle_fix.yml to updated Ansible format if needed
   - Update any deprecated Ansible syntax

2. **Testing Framework** (Moderate complexity)
   - Decide on testing approach (maintain InSpec or migrate to Ansible-native)
   - Set up Molecule for Ansible role testing if replacing Test Kitchen

3. **Chef Deployment Scripts** (High complexity)
   - Create Ansible roles to replace Chef Automate and Chef Infra Server deployment
   - Implement alternative compliance platform deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The compliance testing functionality is more important to preserve than the specific tools used.
3. The organization is moving toward an Ansible-only approach and wants to eliminate Chef dependencies where possible.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
5. The target environment will continue to be Ubuntu-based systems.
6. The migration will maintain the same level of security hardening and compliance testing capabilities.