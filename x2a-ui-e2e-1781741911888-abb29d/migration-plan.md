# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used for compliance automation alongside Ansible deployments. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The primary migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Updating the deployment scripts to use Ansible instead of shell scripts
3. Ensuring all compliance requirements are maintained in the new implementation

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS server configuration and content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML content for the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible testing:
  - Molecule provides similar functionality but is designed specifically for Ansible roles and playbooks
  - Can use the same Vagrant driver for local testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks:
  - Create roles for system preparation (hostname, sysctl settings)
  - Use Ansible's package management modules instead of curl/gunzip commands

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and only enables TLSv1.2
  - Approach: Ensure the Apache SSL module configuration is identical in the migrated Ansible playbooks

- **SSH Security**: The SSH root login check must be preserved
  - Approach: Convert the InSpec control to an Ansible task that validates the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

- **Certificate Management**: Self-signed certificates are generated in the playbook
  - Approach: Maintain the same OpenSSL module usage but consider integrating with Ansible Vault for key storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the detailed InSpec tests to equivalent Ansible validation
  - Mitigation: Use a combination of Ansible's `uri` module for HTTP checks and custom modules or command execution for SSL validation

- **Compliance Metadata**: InSpec tests include detailed compliance metadata (STIG IDs, CCI numbers)
  - Mitigation: Preserve this metadata in Ansible task documentation or use a structured format like YAML comments

- **Test Kitchen Integration**: Replacing the Test Kitchen workflow
  - Mitigation: Document the new Molecule-based testing approach thoroughly for team adoption

### Migration Order

1. **website_https.yml and poodle_fix.yml** (Priority 1, low risk)
   - Already in Ansible format, minimal changes needed
   - Update to use Ansible best practices and remove any deprecated syntax

2. **Chef InSpec Tests** (Priority 2, moderate complexity)
   - Convert to Ansible-native testing solutions
   - Ensure all compliance checks are maintained

3. **Chef Deployment Scripts** (Priority 3, moderate complexity)
   - Convert shell scripts to Ansible playbooks
   - Implement secure credential management

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance validation
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. There is no requirement to maintain backward compatibility with Chef tools
4. The deployment scripts for Chef Automate/Infra Server are no longer needed in their current form
5. The security requirements (SSL/TLS configuration, SSH hardening) must be maintained
6. No external integrations or dependencies beyond what's visible in the repository
7. The migration will consolidate all testing and deployment into a single technology (Ansible)