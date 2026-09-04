# MIGRATION FROM CHEF INSPEC + ANSIBLE TO PURE ANSIBLE

This repository contains a hybrid Chef InSpec and Ansible demonstration setup that showcases compliance automation workflows. The migration involves consolidating the testing and configuration management into a pure Ansible solution with integrated compliance checking. The scope is limited but requires careful consideration of testing methodologies and compliance frameworks.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (demonstration code, no production dependencies)

## Module Migration Plan

This repository contains Chef InSpec compliance tests alongside Ansible playbooks that need consolidation into a unified Ansible-based solution:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host management for a test website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible Playbook
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, HTML content deployment, service management with handlers

**ssl-security-hardening**:
- Description: SSL/TLS security hardening configuration that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible Playbook
- Key Features: POODLE vulnerability mitigation, SSL protocol configuration, Apache SSL module management

**compliance-verification-https**:
- Description: InSpec compliance tests for HTTPS website functionality, SSL protocol validation, and security posture verification
- Path: chef-and-ansible/tests/website_https_verify.rb
- Technology: Chef InSpec
- Key Features: Port 443 listening verification, HTTPS response validation, SSL protocol compliance checks (SSL3 disabled, TLS1.2 enabled)

**ssh-security-compliance**:
- Description: InSpec compliance profile for SSH security configuration focusing on root login restrictions
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec  
- Key Features: SSH root login verification, STIG compliance checks (RHEL-08-000227), security control validation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `chef-and-ansible/index.html`: Static HTML content for website testing
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for lab environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing modules (uri, assert, service_facts) and ansible-lint for compliance
- **Test Kitchen**: Replace with molecule for Ansible role testing and validation
- **Vagrant Driver**: Maintain Vagrant for local testing or migrate to container-based testing with molecule-docker

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL Ansible modules - maintain this approach but consider adding certificate validation tasks
- **SSH Security Compliance**: Convert InSpec SSH controls to Ansible tasks that both configure and verify SSH security settings
- **Credential Management**: No hardcoded credentials detected in current playbooks - maintain this security posture
- **STIG Compliance**: Current SSH profile references RHEL-08-000227 STIG control - ensure Ansible implementation maintains compliance mapping

### Technical Challenges

- **InSpec to Ansible Testing Migration**: Converting Ruby-based InSpec controls to Ansible native testing requires restructuring test logic from external verification to inline task validation
- **Compliance Framework Integration**: Maintaining STIG compliance references and control mappings when migrating from InSpec's structured compliance format to Ansible tasks
- **Test Kitchen Replacement**: Migrating from Test Kitchen's mature testing framework to Molecule requires reconfiguring test scenarios and verification methods

### Migration Order

1. **apache-https-website** (Priority 1: Already in Ansible, requires minimal changes)
2. **ssl-security-hardening** (Priority 1: Simple Ansible playbook, low risk)  
3. **compliance-verification-https** (Priority 2: Requires InSpec to Ansible test conversion)
4. **ssh-security-compliance** (Priority 3: Complex STIG compliance mapping and verification logic)

### Assumptions

- The target environment will continue to use Ubuntu 20.04 LTS as specified in the current Test Kitchen configuration
- Vagrant-based local testing will be maintained or replaced with equivalent container-based testing
- STIG compliance requirements (specifically RHEL-08-000227) need to be preserved in the Ansible implementation despite the Ubuntu target platform
- The demonstration nature of this repository allows for testing methodology changes without production impact concerns
- Self-signed certificate generation is acceptable for the test environment and does not require CA-signed certificates
- The Chef Automate deployment scripts in setup-automate/ are for lab infrastructure only and may not require migration if the focus is purely on the compliance automation workflows
- No external Chef Supermarket cookbook dependencies exist that would complicate the migration
- The current Apache 2.4.41 version pinning in the playbook should be maintained or updated to a current security-patched version
- Test verification will move from post-deployment InSpec runs to inline Ansible task validation and assertions