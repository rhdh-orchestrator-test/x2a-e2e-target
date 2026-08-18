# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be primarily a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance automation, along with scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec test profiles to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format or are simple deployment scripts that can be converted to Ansible roles.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec profiles that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec profile for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile for verifying SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Static HTML file used in the website example. Migration consideration: Keep as-is or include as a template in Ansible role.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Keep InSpec but call it from Ansible using the command module

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (as in the poodle_fix.yml)
  - Consider adding more modern security headers
  - Update to use Let's Encrypt instead of self-signed certificates where possible

- **SSH Security**: The InSpec profile checks for SSH root login configuration. Migration should:
  - Incorporate these checks into Ansible roles
  - Add additional SSH hardening measures

- **Vault/secrets management**:
  - The current repository has hardcoded credentials in the deployment scripts (username, password)
  - Migration should use Ansible Vault to secure these credentials
  - Count of credentials detected: 3 (username, password, email) in each deployment script

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks may require additional logic and different syntax.
  - Mitigation: Create a mapping of InSpec resources to Ansible modules and gradually convert each test.

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible roles.
  - Mitigation: Create an Ansible role that performs the same steps as the bash scripts, using Ansible's package, command, and template modules.

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (convert to Ansible assertions or Molecule tests, moderate complexity)
4. **Deployment Scripts** (convert to Ansible roles, moderate complexity)

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment.
2. The InSpec tests are used for validation and compliance checking, not for continuous monitoring.
3. The deployment scripts are used for setting up test environments, not for production deployments.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
5. The target environment for migration will continue to be Ubuntu 20.04 or similar Linux distributions.
6. The migration will maintain the same functionality but improve security and maintainability.
7. Test Kitchen is used for local development and testing, not for CI/CD pipelines.