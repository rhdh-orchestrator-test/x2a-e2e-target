# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port testing, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server functionality

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to Ansible roles with test tasks

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Security**: The SSH security controls tested by the InSpec profile need to be implemented in Ansible
  - Ensure PermitRootLogin is properly configured
  - Maintain compliance with security standards referenced in the InSpec test (SRG-OS-000112, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - These should be migrated to Ansible Vault or another secure secret management solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules
  - The SSL protocol verification tests are particularly specialized and may require custom implementation in Ansible

- **Chef Automate Deployment**: The Chef Automate and Chef Infra Server deployment scripts will need to be completely reimagined as Ansible roles
  - This will require knowledge of Chef Automate's architecture and deployment requirements
  - Consider whether Chef Automate is still needed or if it should be replaced with an Ansible-native solution

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing)
4. **Chef Deployment Scripts** (high complexity, requires complete rewrite)

### Assumptions

1. The primary goal is to migrate all functionality to pure Ansible without relying on Chef components
2. The InSpec tests are being used for compliance validation and their functionality needs to be preserved
3. The deployment scripts for Chef Automate and Chef Infra Server may be replaced with equivalent Ansible roles or may be deprecated if Chef components are no longer needed
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
5. The security requirements and compliance standards referenced in the InSpec tests must be maintained
6. The repository appears to be a demonstration/example repository rather than production code, but migration should still maintain all functionality
7. No external dependencies or complex integrations are present beyond what's visible in the repository