# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The repository appears to be primarily focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance testing, rather than being a full-fledged infrastructure-as-code repository.

The migration scope is relatively small, focusing on:
1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

Given the limited scope and the fact that part of the codebase is already in Ansible, this migration is estimated to be low complexity and could be completed within 1-2 weeks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and shell scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Static HTML file for the web server. Migration consideration: Include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (as in the current poodle_fix.yml)
  - Consider adding more modern security headers
  - Update SSL configuration to current best practices

- **SSH Security**: The InSpec profile checks for SSH root login. Migration should:
  - Incorporate SSH hardening into Ansible roles
  - Maintain compliance with security standards referenced in the InSpec profile (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Chef Automate Deployment**: The shell scripts deploy Chef Automate and Chef Infra Server, which won't be needed in an Ansible-only environment.
  - Mitigation: Determine if an alternative compliance and reporting solution is needed to replace Chef Automate functionality

### Migration Order

1. **website-https** and **poodle-fix** playbooks (low risk, already in Ansible)
   - Consolidate into a single role for Apache HTTPS configuration
   - Improve variable usage and templating

2. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

3. **Chef deployment scripts** (evaluate necessity)
   - Determine if these need to be migrated or if they're no longer needed
   - If needed, convert to Ansible roles for deployment of alternative compliance tools

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, as indicated by the README.md mentioning "working examples" and "companions to a Progress Chef white paper".

2. The InSpec tests are valuable and need to be preserved in some form, rather than discarded.

3. The Chef Automate and Chef Infra Server deployment scripts may not be needed in the target environment if moving entirely to Ansible.

4. The current Ansible playbooks are functional and follow reasonable practices, so they can be used as a starting point rather than being completely rewritten.

5. The security standards referenced in the InSpec profiles (e.g., SRG-OS-000112) are still relevant and should be maintained in the migrated solution.