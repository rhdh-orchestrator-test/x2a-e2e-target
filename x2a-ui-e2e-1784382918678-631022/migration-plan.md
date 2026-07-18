# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS. Migration considerations include preserving SSL certificate generation, virtual host configuration, and ensuring proper service restarts.

- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability by enforcing TLSv1.2. Migration considerations include ensuring this security fix is maintained in the new Ansible structure.

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with pure Ansible testing framework or adapting to use Molecule.

- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration considerations include converting to Ansible test framework or maintaining InSpec as a testing tool.

- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec as a testing tool.

- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible playbook for deploying alternative compliance platforms.

- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Migration considerations include replacing with Ansible playbook for deploying alternative infrastructure management platforms.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package management in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a standalone testing tool integrated with Ansible workflows
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
- **Chef Automate/Infra Server**: Replace with alternative compliance and infrastructure management platforms like:
  - AWX/Ansible Tower for infrastructure management
  - Compliance solutions like OpenSCAP or maintain InSpec as a standalone tool

### Security Considerations

- **SSL/TLS Configuration**: Maintain the security hardening from poodle_fix.yml to ensure TLSv1.2 is enforced
- **Self-signed Certificates**: Preserve the certificate generation logic but consider enhancing with Let's Encrypt integration
- **SSH Hardening**: Ensure the SSH security controls tested by ssh_profile.rb are implemented in Ansible
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count: 2 sets of credentials detected (user login and SSL certificates)

### Technical Challenges

- **Compliance Testing**: Determining whether to maintain InSpec for compliance testing or migrate to an Ansible-native solution. Mitigation: Consider a hybrid approach where Ansible handles infrastructure provisioning while InSpec remains for compliance testing.

- **Test Framework Migration**: Converting Test Kitchen workflow to Molecule or another Ansible-native testing framework. Mitigation: Create a parallel testing structure with Molecule while maintaining existing tests during transition.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already in Ansible format, focus on restructuring to follow best practices
2. **Testing Framework** (chef-and-ansible/kitchen.yml): Moderate complexity, convert to Molecule or enhance existing Ansible testing
3. **Chef Deployment Scripts** (setup-automate/*.sh): Higher complexity, replace with Ansible playbooks for alternative platforms

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec compliance testing with Ansible, not to provide production-ready infrastructure.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. The security configurations (SSL/TLS, SSH) are critical to maintain in the migration.
4. There is no existing Ansible inventory or host configuration beyond what's in the kitchen.yml file.
5. The Chef Automate and Chef Infra Server deployment scripts are used for demonstration purposes and may not need direct migration if alternative compliance platforms are chosen.
6. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced with secure credential management in production.