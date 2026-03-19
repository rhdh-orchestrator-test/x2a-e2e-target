# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving Chef InSpec tests and Ansible playbooks for web server configuration. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile for validating HTTPS website configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for web server testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for infrastructure testing
  - Option 2: Use simple Vagrant or Docker-based testing with custom scripts

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening for SSL/TLS protocols
  - Ensure the POODLE vulnerability fix (disabling SSLv3) is preserved
  - Maintain TLSv1.2 requirement in the migrated configuration

- **SSH Security**: Preserve the SSH security controls
  - Maintain the restriction on root login via SSH
  - Preserve STIG compliance metadata for auditing purposes

- **Self-signed Certificates**: Consider improving the certificate management
  - Option 1: Integrate with Ansible Vault for certificate storage
  - Option 2: Use Let's Encrypt for production environments

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to equivalent Ansible testing framework
  - Challenge: Preserving the compliance metadata and controls
  - Mitigation: Use Ansible Molecule with custom verifiers or maintain InSpec as a separate tool

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure deployment scripts
  - Challenge: Determining if Chef Automate/Server is still needed or if it should be replaced with Ansible Tower/AWX
  - Mitigation: Create equivalent Ansible playbooks for deploying Ansible Tower/AWX if needed

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need refactoring to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires conversion to Ansible testing framework
3. **Chef Infrastructure** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires strategic decision on whether to replace with Ansible Tower/AWX

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes rather than production use
2. The InSpec tests are used for compliance validation of infrastructure configured by Ansible
3. The Chef Automate and Chef Server deployment scripts may not be needed in an Ansible-only environment
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. Vagrant will continue to be used for development/testing environments
6. The security requirements (SSL/TLS configuration, SSH hardening) must be maintained in the migrated solution
7. The migration will preserve the ability to validate compliance with security standards (e.g., STIG)