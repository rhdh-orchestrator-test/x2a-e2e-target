# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

**Complexity**: Low to Medium - The repository contains a limited number of files with clear purposes, but requires careful handling of security testing and compliance validation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test for validating HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework configuration
- `index.html`: Sample HTML file used in the web server deployment - can be preserved as-is

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's `assert` module for basic validation
  - Option 2: Molecule for comprehensive testing
  - Option 3: Ansible Lint for static analysis
  - Option 4: Convert InSpec tests to Python-based tests using pytest

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 is enforced
  - Maintain disabling of vulnerable protocols

- **SSH Security**: Preserve the SSH root login security check
  - Convert the InSpec control to equivalent Ansible validation
  - Maintain STIG compliance metadata

- **Certificate Management**: Preserve the self-signed certificate generation
  - Ensure proper permissions on certificate files (mode: 0640)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's `assert` module with clear documentation of test intent
  - Consider using Molecule for more comprehensive testing

- **Compliance Metadata**: Preserving STIG and CCI compliance metadata from InSpec tests
  - Mitigation: Add compliance metadata as comments or variables in Ansible playbooks
  - Consider using Ansible tags to mark compliance-related tasks

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Mitigation: Evaluate AWX/Tower for compliance reporting or integrate with external compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible playbooks
4. **Test Infrastructure** (kitchen.yml) - Replace with Molecule configuration

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. The security requirements (TLS configuration, SSH hardening) will remain the same
4. The team is willing to adopt Ansible-native testing tools in place of InSpec
5. There is no requirement to maintain backward compatibility with Chef InSpec
6. The Chef Automate and Chef Infra Server deployment is for testing/development purposes and not production, given the hardcoded credentials