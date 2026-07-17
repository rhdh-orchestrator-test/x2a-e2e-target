# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to medium, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **https-compliance-tests**:
    - Description: Chef InSpec tests that verify HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification

- **ssh-compliance-profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Server installation, user and organization creation

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, Chef Server integration

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment - can be reused as-is in Ansible content

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Option 1: Deploy alternative compliance platforms like Ansible Tower/AWX
  - Option 2: Deploy open-source alternatives for compliance reporting

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache security hardening that includes the SSL/TLS configurations

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Approach: Create an Ansible role for certificate management with options for both self-signed and proper CA-signed certificates

- **SSH Hardening**: The SSH compliance profile checks for secure SSH configurations
  - Approach: Create an Ansible role that applies the same SSH hardening measures being tested

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec's testing capabilities
  - Mitigation: Evaluate and implement a combination of Ansible assert, Molecule, and potentially custom modules to achieve the same level of compliance testing

- **Test Execution Flow**: The current setup uses Test Kitchen to orchestrate the test flow
  - Mitigation: Implement CI/CD pipelines using GitHub Actions or similar to replace the Test Kitchen workflow

- **Maintaining Compliance Standards**: The InSpec profiles reference specific compliance standards (e.g., SRG-OS-000112)
  - Mitigation: Document the mapping between InSpec controls and Ansible checks to maintain traceability to compliance standards

### Migration Order

1. **website-https-configuration** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role with variables

2. **poodle-vulnerability-fix** (low risk, already Ansible)
   - Integrate into the HTTPS website role as a security enhancement option

3. **chef-server-deployment** and **chef-automate-deployment** (medium complexity)
   - Create Ansible playbooks to replace the shell scripts
   - Implement Ansible Vault for credential storage

4. **https-compliance-tests** and **ssh-compliance-profile** (high complexity)
   - Develop Ansible-based testing approach
   - Implement equivalent checks using Ansible's testing tools

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation, not to provide production-ready infrastructure code
2. The InSpec tests are the most valuable components to preserve in terms of functionality
3. The deployment scripts for Chef Server and Automate will be replaced with equivalent Ansible functionality or alternative compliance platforms
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The migration will maintain the same level of security hardening present in the original code
6. No external dependencies or integrations beyond what's visible in the repository need to be considered