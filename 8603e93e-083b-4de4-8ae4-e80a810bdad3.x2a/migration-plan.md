# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Chef InSpec profiles for compliance testing
2. Ansible playbooks for web server configuration
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The primary focus will be on converting the Chef InSpec profiles to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks and enhancing them with the functionality currently provided by the Chef components.

## Module Migration Plan

This repository contains Chef InSpec profiles and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for testing web server configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible's `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Integrate with pytest-ansible for advanced testing scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or retain Test Kitchen with the `kitchen-ansible` plugin if preferred

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI, role-based access control, and job scheduling
  - Ansible Galaxy for role sharing
  - GitLab CI/GitHub Actions for CI/CD pipelines

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Migration approach: Convert directly to Ansible tasks with identical functionality

- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be implemented as Ansible tasks
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Create a mapping of InSpec resources to Ansible modules and develop templates for common test patterns

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Mitigation: Implement AWX/Tower with custom reporting dashboards or integrate with compliance tools like OpenSCAP

- **User Management**: Replicating Chef Server's user and organization management
  - Mitigation: Implement RBAC in AWX/Tower and use Ansible for user management tasks

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Add documentation and variable parameterization

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Replace with Ansible playbooks for AWX/Tower deployment
   - Implement user management through Ansible

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible integration, not for production deployment
2. The Chef components are mainly used for compliance testing, not for configuration management
3. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
4. The migration will preserve all security controls and compliance checks
5. No external data sources or complex integrations are present beyond what's visible in the repository
6. The Apache web server configuration is relatively simple and can be directly migrated
7. User management requirements are basic and can be handled by AWX/Tower or similar tools