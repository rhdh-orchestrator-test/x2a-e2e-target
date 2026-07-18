# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations, with a focus on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible-playbooks**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and SSL security hardening
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache HTTPS configuration, SSL certificate generation, POODLE vulnerability mitigation

- **chef-and-ansible-tests**:
    - Description: Chef InSpec test profiles for verifying HTTPS and SSH configurations
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH security compliance checks

- **setup-automate-scripts**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS. Migration considerations include preserving the SSL certificate generation, virtual host configuration, and Apache module management.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2. Migration considerations include ensuring this security hardening is maintained.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with equivalent Ansible testing framework or adapting to use Ansible's native testing capabilities.
  
- `chef-and-ansible/index.html`: Simple HTML file used as a template for the website. Migration considerations include preserving this content in the Ansible template.
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration. Migration considerations include converting to Ansible test framework or maintaining InSpec as a testing tool alongside Ansible.
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec as a testing tool alongside Ansible.
  
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible playbook for deploying alternative compliance and infrastructure management tools.
  
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Migration considerations include replacing with Ansible playbook for deploying alternative infrastructure management tools.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version 2.4.41-4ubuntu3.10)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on comments in setup scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Options:
  1. Replace with Ansible-native testing using assert, fail, and debug modules
  2. Maintain InSpec as a complementary testing tool alongside Ansible (recommended)
  3. Explore alternative compliance tools like Ansible Lint or Molecule

- **Test Kitchen**: Currently used for testing Ansible playbooks. Replace with:
  1. Ansible Molecule for testing playbooks
  2. Simple Vagrant-based testing workflow with Ansible provisioner

- **Chef Automate/Infra Server**: Currently deployed via shell scripts. Replace with:
  1. Ansible playbooks to deploy alternative compliance and infrastructure management tools
  2. Consider AWX/Ansible Tower as a replacement for Chef Automate's dashboard functionality

### Security Considerations

- **SSL/TLS Configuration**: The current implementation properly disables SSLv3 and enables only TLSv1.2. This security hardening must be maintained in the migrated solution.
  
- **Self-signed Certificates**: The current implementation generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
  
- **SSH Hardening**: The SSH compliance profile checks for root login restrictions. Ensure this security check is maintained and implemented in the Ansible configuration.
  
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in setup scripts (username/password in deploy-automate.sh and deploy-chef-server.sh)

### Technical Challenges

- **Compliance Testing**: The repository demonstrates using Chef InSpec for compliance testing with Ansible. The migration needs to either:
  1. Maintain this hybrid approach (Ansible for configuration, InSpec for testing)
  2. Replace InSpec with Ansible-native testing capabilities
  
  Mitigation strategy: Start with maintaining the hybrid approach while developing equivalent Ansible testing capabilities in parallel.

- **Chef Automate Replacement**: Chef Automate provides compliance dashboards and reporting that need equivalent functionality.
  
  Mitigation strategy: Evaluate AWX/Ansible Tower or other open-source alternatives that can provide similar compliance reporting capabilities.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk, already in Ansible format, only need minor adjustments to follow best practices
2. **Testing Framework** (chef-and-ansible/tests/*): Moderate complexity, requires decision on testing approach
3. **Chef Deployment Scripts** (setup-automate/*): High complexity, requires architectural decisions on replacement tools

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec compliance testing with Ansible, not to provide production-ready infrastructure.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. The security hardening (POODLE fix, SSH restrictions) is a critical requirement that must be maintained.
4. The Chef Automate and Chef Infra Server deployment scripts are used for demonstration purposes and may not reflect production deployment patterns.
5. There is no existing state or data that needs to be preserved during migration.
6. The migration will consolidate to pure Ansible where possible, but may maintain Chef InSpec for compliance testing if that provides the best solution.