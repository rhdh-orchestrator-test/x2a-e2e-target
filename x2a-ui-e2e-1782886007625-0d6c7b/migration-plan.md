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
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

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
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in compliance capabilities

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced in the migrated Ansible configuration
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: The SSH root login check must be maintained
  - Convert the InSpec control to an Ansible task that checks the same configuration
  - Consider implementing remediation in addition to checking

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Consider enhancing with Let's Encrypt integration for production environments
  - Maintain the same certificate generation process if self-signed is still required

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the modules

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Challenge: InSpec has specific testing capabilities that may not have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible assert, command modules, and potentially external testing tools

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible management
  - Challenge: The Chef Server deployment scripts create users and organizations that need equivalent functionality
  - Mitigation: Set up Ansible Tower/AWX with similar user/organization structure

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better reusability

2. **poodle_fix.yml** (low risk, already Ansible)
   - Integrate into the website_https role as a security enhancement
   - Update to include more current security best practices

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible security checks

4. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible Tower/AWX deployment playbooks
   - Or convert to Ansible playbooks for deploying alternative orchestration tools

### Assumptions

1. The current implementation is primarily for demonstration/testing purposes rather than production use, given the self-signed certificates and test-oriented structure.

2. The InSpec tests are being used for compliance verification rather than traditional unit/integration testing.

3. The deployment scripts are templates that would be customized for actual deployments (given the placeholder values).

4. The migration target is a pure Ansible environment without any Chef components.

5. The current Test Kitchen setup is used for development and testing, not for production deployments.

6. The SSH compliance check is part of a larger compliance framework that isn't fully represented in this repository.

7. The Apache configuration is relatively simple and doesn't include complex customizations that might be challenging to migrate.