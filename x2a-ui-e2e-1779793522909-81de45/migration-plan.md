# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a pure Chef cookbook repository. The migration scope is relatively small, focusing on:

1. Chef InSpec test profiles that need to be maintained or migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Server deployment scripts that need to be converted to Ansible playbooks

The estimated timeline for migration is short (1-2 weeks) due to the limited scope and the fact that some components are already using Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for verifying HTTPS website configuration, port status, and SSL/TLS protocol compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: HTTP response validation, SSL/TLS protocol verification, port listening checks

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration validation
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, CCI compliance mapping, STIG validation

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: User and organization creation, system configuration, Chef Automate deployment

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: User and organization creation, system configuration, Chef Server deployment

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `website_https.yml`: Ansible playbook for configuring HTTPS website with Apache
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability in Apache
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Maintain InSpec as a standalone testing tool and integrate with Ansible workflows

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that:
  - Configure system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
  - Set hostname
  - Deploy equivalent monitoring and compliance solutions (e.g., AWX/Tower, Prometheus, Grafana)

### Security Considerations

- **SSH Security Controls**: The SSH compliance profile checks need to be maintained:
  - Migrate InSpec SSH controls to Ansible security roles or collections
  - Consider using ansible-lockdown or similar security-focused collections

- **SSL/TLS Configuration**: Maintain security hardening for web servers:
  - The POODLE vulnerability fix needs to be incorporated into the Ansible roles
  - Ensure TLS 1.2+ is enforced and older protocols are disabled

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation and management should use Ansible's crypto modules

### Technical Challenges

- **Testing Framework Migration**: Moving from InSpec to Ansible-native testing:
  - Challenge: InSpec provides specialized resources for compliance testing
  - Mitigation: Use Ansible assert modules or maintain InSpec as a complementary tool

- **Compliance Reporting**: Maintaining compliance reporting capabilities:
  - Challenge: Chef Automate provides built-in compliance reporting
  - Mitigation: Integrate with tools like Prometheus/Grafana or AWX/Tower for reporting

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Already in Ansible format, no migration needed
2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks
3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible testing framework or maintain as-is with integration points

### Assumptions

1. The repository is primarily demonstrating how Chef InSpec can work alongside Ansible rather than being a pure Chef cookbook repository
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. The deployment scripts are templates that would be customized for actual deployments
4. Security compliance testing is a primary concern for the migration
5. The hardcoded credentials in deployment scripts are for demonstration purposes only
6. The repository does not contain actual Chef cookbooks that need migration, only InSpec tests and deployment scripts